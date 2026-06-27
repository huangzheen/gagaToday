"""
Wikipedia / Wikidata / Brave Search 服务
用于场景介绍生成 — 自动跨语言抓取 + LLM 改写/翻译

流程:
1. Wikipedia DE 摘要(主要来源,如有)
2. 如有 DE → 查 Wikidata QID → 拿 ZH/EN sitelink → 各自拉摘要
3. 任何缺失语言 → LLM 翻译 DE 原文补齐
4. 若 DE 完全无 → Brave Search 搜德语内容 → 取第一条 snippet
"""

import json
import urllib.parse
import urllib.request
from typing import Optional

from .llm_service import generate_text
from ..config import BRAVE_API_KEY, BRAVE_SEARCH_URL, LLM_MODEL_DEFAULT


# ── HTTP helpers ──
_UA = "gagaToday-POIGenerator/1.0 (educational use)"


def _http_get_json(url: str, headers: dict = None, timeout: int = 10) -> Optional[dict]:
    """简单 GET + JSON,失败返回 None"""
    req = urllib.request.Request(url, headers={"User-Agent": _UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


# ── Wikipedia / Wikidata ──


def _de_wikipedia_api() -> str:
    return "https://de.wikipedia.org/w/api.php"


def _wikidata_api() -> str:
    return "https://www.wikidata.org/w/api.php"


def get_wikidata_qid(name_de: str, location_hint: str = None) -> Optional[str]:
    """从德语维基百科标题拿 Wikidata QID(如 'Frauenkirche' → 'Q167193')

    优先用 Wikidata 自己的 wbsearchentities(按相关性排序,自带 description),
    配合 location_hint 过滤('München' 城市条目优先)。
    """
    if not name_de:
        return None

    # ── Step 1: 尝试直接从 DE 维基百科拿 wikibase_item(适用于无歧义的情况) ──
    qs = urllib.parse.urlencode({
        "action": "query",
        "prop": "pageprops",
        "titles": name_de,
        "format": "json",
    })
    data = _http_get_json(f"{_de_wikipedia_api()}?{qs}")
    if data:
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            qid = page.get("pageprops", {}).get("wikibase_item")
            if not qid:
                continue
            title = page.get("title", "")
            is_disambig = (
                "(Begriffsklärung)" in title
                or title.startswith("Liste ")
                or page.get("pageprops", {}).get("disambiguation") is not None
            )
            if not is_disambig:
                return qid

    # ── Step 2: 用 Wikidata wbsearchentities(自带 description 和相关性排序) ──
    hint = location_hint if location_hint else "München"
    qs = urllib.parse.urlencode({
        "action": "wbsearchentities",
        "search": name_de,
        "language": "de",
        "type": "item",
        "limit": 10,
        "format": "json",
    })
    data = _http_get_json(f"{_wikidata_api()}?{qs}")
    if not data:
        return None

    # 评分候选:精确名字匹配 +10,hint 在 description 中 +5
    best_qid = None
    best_score = -1
    for hit in data.get("search", []):
        label = (hit.get("label") or "").strip()
        desc = (hit.get("description") or "").lower()
        qid = hit.get("id")
        if not qid:
            continue
        score = 0
        # label 与 name_de 完全匹配 → 强信号
        if label.lower() == name_de.lower():
            score += 20
        elif label.lower().startswith(name_de.lower()):
            score += 10
        elif name_de.lower() in label.lower():
            score += 5
        # description 含 hint(如 'Munich' / 'square in Munich') → 强烈暗示是当地条目
        if hint and (hint.lower() in desc or "munich" in desc or "münchen" in desc):
            score += 8
        # 减分:description 是 'building' / 'street' / 'station' 等非地标类型
        for noise in ("building", "straße", "street", "station", "light rail", "wohn"):
            if noise in desc:
                score -= 3
        if score > best_score:
            best_score = score
            best_qid = qid

    if best_score > 0:
        return best_qid
    return None


def get_sitelinks_for_qid(qid: str) -> dict[str, str]:
    """从 Wikidata QID 拿各语言维基百科标题
    返回 {'de': 'Frauenkirche', 'zh': '圣母教堂', 'en': 'Frauenkirche', ...}
    """
    if not qid:
        return {}
    qs = urllib.parse.urlencode({
        "action": "wbgetentities",
        "ids": qid,
        "props": "sitelinks",
        "format": "json",
    })
    data = _http_get_json(f"{_wikidata_api()}?{qs}")
    if not data:
        return {}
    entity = data.get("entities", {}).get(qid, {})
    sitelinks = entity.get("sitelinks", {})
    out = {}
    for site, info in sitelinks.items():
        # 'dewiki' → 'de', 'zhwiki' → 'zh', 'enwiki' → 'en', etc.
        if site.endswith("wiki"):
            lang = site[:-4]
            out[lang] = info.get("title")
    return out


def fetch_wikipedia_summary(lang: str, title: str, max_chars: int = 1800) -> Optional[dict]:
    """拉维基百科介绍 — 拿前 max_chars 字符(lead + 第一段内容)
    MediaWiki API 的 exchars 参数行为诡异(设 2000/3000/5000 都只返 ~1200),
    所以改用拉全文章 + Python 切片。
    max_chars=1800 ≈ 280 词,拿 lead + 第一段 Geschichte 等内容,够丰富但不是全文。
    返回 {'title', 'extract', 'url'} 或 None(404)
    """
    if not lang or not title:
        return None
    # 拉全文(不限制),Python 端切片更可控
    qs = urllib.parse.urlencode({
        "action": "query",
        "prop": "extracts",
        "explaintext": "1",
        "redirects": "1",
        "titles": title,
        "format": "json",
    })
    api_url = f"https://{lang}.wikipedia.org/w/api.php?{qs}"
    data = _http_get_json(api_url)
    if not data:
        return None
    pages = data.get("query", {}).get("pages", {})
    extract = ""
    page_title = title
    for page in pages.values():
        extract = page.get("extract", "")
        page_title = page.get("title", title)
        break
    if not extract:
        return None
    # 切成前 max_chars 字符,在段末/句末截止,避免切碎半句
    if len(extract) > max_chars:
        cut = extract[:max_chars]
        # 优先在 \n\n (段末) 切;其次 \n (维基百科段间空行);其次 ". " (英文/德文句末)
        for sep in ["\n\n", "\n", ". ", "。 "]:
            idx = cut.rfind(sep)
            if idx > max_chars * 0.7:  # 至少保留 70% 内容
                if sep == "\n\n":
                    extract = cut[:idx]
                else:
                    extract = cut[:idx + len(sep)].strip()
                break
        else:
            # 实在找不到合适的切点,直接用 max_chars
            extract = cut
    # URL 用 REST summary(包含 redirects 信息,更准)
    safe = urllib.parse.quote(title.replace(" ", "_"), safe="")
    rest_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{safe}"
    rest_data = _http_get_json(rest_url)
    page_url = ""
    if rest_data:
        page_url = rest_data.get("content_urls", {}).get("desktop", {}).get("page", "")
    if not page_url:
        page_url = f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(page_title.replace(' ', '_'))}"
    return {
        "title": page_title,
        "extract": extract.strip(),
        "url": page_url,
    }


# ── Brave Search fallback ──


def brave_search_de(query: str, count: int = 3) -> list[dict]:
    """Brave Search — DE locale,Wikipedia/官方源优先
    返回 [{'title', 'url', 'description'}, ...]
    """
    if not BRAVE_API_KEY or not query:
        return []
    qs = urllib.parse.urlencode({
        "q": query,
        "count": count,
        "country": "DE",
        "search_lang": "de",
        "ui_lang": "de",
        "safesearch": "moderate",
    })
    data = _http_get_json(
        f"{BRAVE_SEARCH_URL}?{qs}",
        headers={"X-Subscription-Token": BRAVE_API_KEY, "Accept": "application/json"},
    )
    if not data:
        return []
    results = []
    for r in (data.get("web", {}) or {}).get("results", []):
        results.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "description": r.get("description", ""),
        })
    return results


# ── LLM helpers ──


def _looks_like_disambig(summary: dict) -> bool:
    """检测维基百科摘要是不是消歧义(disambig)页面

    只用高精度信号,避免 'following' / 'is the name of' 等通用词误判。
    注意:'following' 在常规文章里很常见(例:'following the older church'),
    'ist der name' / 'is the name of' 也会在正常描述中触发,所以不用。
    """
    if not summary:
        return True
    title = (summary.get("title") or "").lower()
    extract = (summary.get("extract") or "").lower()

    # 强信号:标题里就有消歧义标记
    if title.startswith("liste ") or title.startswith("list of "):
        return True
    if "(begriffsklärung)" in title or "(disambiguation)" in title or "(消歧义)" in title:
        return True

    # 内容前 300 字符内的典型模板(只在 lead 段检测,正文不算)
    head = extract[:300]
    for marker in [
        " may refer to:",         # en: "X may refer to:"
        "may refer to the following",  # en
        " steht für:",            # de: "X steht für:"
        " bezeichnen kann:",      # de
        " (begriffsklärung)",     # de (在正文里)
        "this disambiguation page",   # en
        " 消歧义",                # zh
    ]:
        if marker in head:
            return True
    return False
    """按"词数"截断到目标长度(英文/德语按空格,中文按字符)
    优先在句末(。！？.!?\n)切,不切碎半句。
    """
    if not text:
        return ""
    # 中文按字符计 ~60 字(对应 ~100 词)
    is_chinese = any('\u4e00' <= c <= '\u9fff' for c in text)
    if is_chinese:
        max_chars = max_words * 0.6  # 100 词 ≈ 60 中文字
        if len(text) <= max_chars:
            return text
        # 找最近的句末
        cut = text[:int(max_chars)]
        for sep in ["。", "！", "?", "\n"]:
            idx = cut.rfind(sep)
            if idx > max_chars * 0.6:  # 至少保留 60%
                return cut[:idx + 1].strip()
        return cut.strip() + "..."
    else:
        # 英文/德语按空格分词
        words = text.split()
        if len(words) <= max_words:
            return text
        cut_words = words[:max_words]
        # 在最后一个完整句子截止
        cut_text = " ".join(cut_words)
        for sep in [". ", "! ", "? ", "\n"]:
            idx = cut_text.rfind(sep)
            if idx > len(cut_text) * 0.6:
                return cut_text[:idx + len(sep)].strip()
        return cut_text.strip() + "..."


def truncate_to_words(text: str, max_words: int = 120) -> str:
    """按"词数"截断到目标长度(英文/德语按空格,中文按字符)
    优先在句末(。！？.!?\n)切,不切碎半句。
    """
    if not text:
        return ""
    # 中文按字符计 ~60 字(对应 ~100 词)
    is_chinese = any('\u4e00' <= c <= '\u9fff' for c in text)
    if is_chinese:
        max_chars = max_words * 0.6  # 100 词 ≈ 60 中文字
        if len(text) <= max_chars:
            return text
        cut = text[:int(max_chars)]
        for sep in ["。", "！", "?", "\n"]:
            idx = cut.rfind(sep)
            if idx > max_chars * 0.6:
                return cut[:idx + 1].strip()
        return cut.strip() + "..."
    else:
        words = text.split()
        if len(words) <= max_words:
            return text
        cut_text = " ".join(words[:max_words])
        for sep in [". ", "! ", "? ", "\n"]:
            idx = cut_text.rfind(sep)
            if idx > len(cut_text) * 0.6:
                return cut_text[:idx + len(sep)].strip()
        return cut_text.strip() + "..."


def llm_translate_de_to(text_de: str, target_lang: str) -> str:
    """德语原文 → 目标语言翻译 — 保留事实,忠实翻译
    不重写、不编造、不添加氛围描写。只翻。
    """
    if not text_de:
        return ""
    if target_lang == "zh":
        sys_p = (
            "你是德语到中文的精确翻译。保留所有事实信息、地名、人名、历史年代。"
            "忠实翻译,不重写、不添加、不删减。不要加标题或解释。"
        )
        user_p = f"把下列德文翻译成中文(忠实翻译,不重写):\n\n---\n{text_de}\n---\n\n只输出翻译:"
    else:  # en
        sys_p = (
            "You are a precise German-to-English translator. Preserve all facts, names, dates, "
            "and place names. Translate faithfully — do not rewrite, embellish, or add creative "
            "flavor. Output only the translation, no preamble."
        )
        user_p = f"Translate the following German text into English (faithful translation, do not rewrite):\n\n---\n{text_de}\n---\n\nTranslation only:"
    try:
        resp = generate_text(user_p, sys_p, model=LLM_MODEL_DEFAULT, temperature=0.2, max_tokens=800)
        return (resp.get("text") or "").strip()
    except Exception as e:
        print(f"[wiki_service] LLM translate failed ({target_lang}): {e}")
        return ""


# ── 主入口 ──


def fetch_intro(name_de: str, name_zh: str = None, name_en: str = None) -> dict:
    """
    主入口:返回 {de, zh, en} 三语场景介绍 + 来源标注

    Args:
        name_de: 德语地点名(如 'Frauenkirche')
        name_zh: 中文地点名(可选,如 '圣母教堂')
        name_en: 英语地点名(可选)

    Returns:
        {
            "de": "...",
            "zh": "...",
            "en": "...",
            "sources": {"de": "wikipedia"|"web_search"|"llm_rewrite", "zh": "...", "en": "..."},
            "urls": {"de": "...", "zh": "...", "en": "..."},
            "wikidata_qid": "Q461636" or None
        }
    """
    if not name_de:
        return {"de": "", "zh": "", "en": "", "sources": {}, "urls": {}, "wikidata_qid": None}

    sources = {}
    urls = {}
    raw_by_lang = {}  # lang → raw source text

    # ── Step 1: 拿 Wikidata QID(走 search+location_hint 处理消歧) ──
    qid = get_wikidata_qid(name_de, location_hint="München")

    if qid:
        # 有 QID → 用 sitelink 拿所有语言的精确标题,逐个拉摘要(权威来源)
        sitelinks = get_sitelinks_for_qid(qid)
        for lang in ("de", "zh", "en"):
            title_in_lang = sitelinks.get(lang)
            if title_in_lang:
                summary = fetch_wikipedia_summary(lang, title_in_lang)
                if summary and summary["extract"] and not _looks_like_disambig(summary):
                    raw_by_lang[lang] = summary["extract"]
                    urls[lang] = summary["url"]
                    sources[f"{lang}_raw"] = "wikipedia"
    else:
        qid = None
        # 没 QID(连 search 都搜不到) → 试试直接拉 DE 维基
        de_wiki = fetch_wikipedia_summary("de", name_de)
        if de_wiki and de_wiki["extract"] and not _looks_like_disambig(de_wiki):
            raw_by_lang["de"] = de_wiki["extract"]
            urls["de"] = de_wiki["url"]
            sources["de_raw"] = "wikipedia"

    # ── Step 3: DE Wikipedia 缺失 → Brave Search 搜德语内容 ──
    if "de" not in raw_by_lang:
        search_query = name_de + (" " + name_zh if name_zh else "")
        results = brave_search_de(search_query, count=3)
        if results:
            # 取第一条 snippet 作为德语原文
            raw_by_lang["de"] = results[0]["description"] or results[0]["title"]
            urls["de"] = results[0]["url"]
            sources["de_raw"] = "brave_search"
            qid = None  # 没有 Wikidata

    # ── Step 4: 输出处理(直接用维基百科摘要全文,不截断)
    # 关键:不调 LLM 改写,不截断,保留维基百科原文事实。只有翻译走 LLM(缺失语言时)
    out = {"de": "", "zh": "", "en": ""}
    for lang in ("de", "zh", "en"):
        if lang in raw_by_lang:
            out[lang] = raw_by_lang[lang]  # 维基百科原文,多长就多长
            sources[lang] = "wikipedia"

    # ── Step 5: 缺失语言 → LLM 翻译 DE(忠实翻译,不重写) ──
    for lang in ("zh", "en"):
        if not out[lang] and out["de"]:
            out[lang] = llm_translate_de_to(out["de"], lang)
            sources[lang] = "llm_translate"

    # ── Step 6: 同步生成三语 TTS 音频(预生成,玩家点 🔊 零延迟) ──
    # 注: 失败不影响主流程(audio 字段缺失即可,前端按"无音频"处理)
    poi_id_for_audio = _slugify_poi_id(name_de)
    audio = _generate_intro_audio(poi_id_for_audio, out)

    return {
        "de": out["de"],
        "zh": out["zh"],
        "en": out["en"],
        "sources": sources,
        "urls": urls,
        "wikidata_qid": qid,
        "audio": audio,  # {de: {url, ...}, zh: {...}, en: {...}} 或 {}
    }


# ── TTS 集成 ──


def _slugify_poi_id(name: str) -> str:
    """从德语名生成 POI ID slug,用于 audio 文件路径
    'Marienplatz' → 'marienplatz'
    'Schloss Nymphenburg' → 'schloss-nymphenburg'
    """
    import re
    s = name.strip().lower()
    s = re.sub(r"ä", "ae", s)
    s = re.sub(r"ö", "oe", s)
    s = re.sub(r"ü", "ue", s)
    s = re.sub(r"ß", "ss", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "unknown"


def _generate_intro_audio(poi_id: str, intros: dict) -> dict:
    """对三语文本同步调 TTS,返回 {de: {url, duration_estimate, size_bytes}, ...}"""
    from .tts_service import synthesize_intro
    audio = {}
    for lang in ("de", "zh", "en"):
        text = intros.get(lang, "").strip()
        if not text:
            continue
        try:
            r = synthesize_intro(poi_id, lang, text, city="munich")
            if r:
                audio[lang] = {
                    "url": r["url"],
                    "duration_estimate": r["duration_estimate"],
                    "size_bytes": r["size_bytes"],
                }
        except Exception as e:
            print(f"[wiki_service] TTS {poi_id}/{lang} 失败: {e}")
            # 单个 lang 失败不阻断其他
    return audio