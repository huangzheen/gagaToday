"""
OSM 数据提取 API
为素材生成器提供真实地图数据的查询接口
"""

import json
import re
from fastapi import APIRouter, Query, HTTPException
from ..services.osm_extractor import extract_osm_data
from ..services.osm_geocoder import geocode_osm_poi
from ..services.llm_service import generate_text
from ..config import LLM_MODEL_DEFAULT

router = APIRouter(prefix="/api/osm", tags=["osm"])


@router.get("/extract")
async def api_osm_extract(
    lat: float = Query(..., description="纬度"),
    lng: float = Query(..., description="经度"),
    tile_url: str = Query(None, description="PMTiles URL（可选）"),
):
    """
    查询指定坐标的 OSM 地图数据

    返回该位置附近的所有有用信息：
    - primary_poi: 主 POI（名称、类型、多语言翻译）
    - building: 建筑信息（高度、颜色）
    - address: 地址/门牌号
    - transport: 附近交通（U-Bahn、电车）
    - roads: 道路名称
    - nearby_pois: 附近兴趣点
    """
    try:
        result = extract_osm_data(lat, lng, tile_url)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


def _has_cjk(s: str) -> bool:
    """是否包含中日韩字符"""
    return bool(re.search(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]', s))


def _parse_llm_json(text: str) -> dict:
    """从 LLM 输出解析 JSON,容忍 markdown 代码块"""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[-1]
        t = t.rsplit("```", 1)[0].strip()
    if t.startswith("```json"):
        t = t[7:].strip()
        if t.endswith("```"):
            t = t[:-3].strip()
    return json.loads(t)


# ── Agent-resolve: LLM 当 driver,生成多搜索 query + 跑 PMTiles + 合并候选 ──
# 这是为"添加新 POI"弹窗设计的: 用户输入任意语言地名 → LLM 规范化 → 后端搜本地 → 返回 top 5 候选 → 用户选

AGENT_RESOLVE_SYSTEM = """你是 gagaToday 游戏的 POI 查找助手。

## 业务背景
gagaToday 是一款德国留学模拟 RPG 游戏,场景设定在慕尼黑。玩家会在城市中探索真实地标——
博物馆、教堂、广场、火车站、公园等等。游戏需要为每个地点建立"POI 卡片"页面,包含经纬度、
三语介绍(德/中/英)、周边 OSM 数据等。

现在用户在"添加新 POI"弹窗输入了一个地名(可能是中文/德语/英语/其他语言)。你的任务是:
1. 理解用户实际想找的具体地点
2. 把它转换成能在 OpenStreetMap (OSM) 里搜到的德语搜索关键词

## 数据源说明
我们本地有 9GB 的 PMTiles 矢量瓦片(germany-zoom16.pmtiles),覆盖全德国 OSM 数据,
搜索 bbox 默认限定在慕尼黑主城区(lat 48.06-48.25, lng 11.36-11.75)。
搜索范围 z=14,每次扫描 ~250 个 tile,约 200ms 返回。

OSM 里的 POI 名称通常以**德语**为权威名(name_de 字段),也有英语/法语等 name:xx 字段。
中文名(name:zh)覆盖很稀疏,大多只有热门地标才有,且是繁体。

## 你的任务: 把用户输入转换成 1-3 个德语搜索 query

输出 JSON:
{
  "intent_zh": "用户实际想找的地标(用中文简洁表达,1 句)",
  "intent_de": "用户想找的地标(用德语简洁表达,1 句)",
  "search_queries": [
    "最可能的德语完整名称(含城市前缀 München,如果适用)",
    "短名称(去掉城市前缀)",
    "常用别名/缩写(可选,例如 Hbf)"
  ],
  "rationale": "为什么这样切 query(1-2 句,简短)"
}

### 规则
- 中文输入必须翻译成德语。"慕尼黑中央火车站" → ["München Hauptbahnhof", "Hauptbahnhof"]
- 德语/英语输入通常直接保留,但也尝试加/去城市前缀(用户可能输入 "Hauptbahnhof" 也可能 "München Hauptbahnhof")
- 拼写变体: "Hauptbahnhof" 缩写 "Hbf", "Marienplatz" 别名 "Stachus"(Karlsplatz 的别名不要乱加,只在该地标本身有别名时)
- 第一项必须是最完整最可能的名称(含 München)
- 不要超过 3 个 query,避免冗余
- 不要输出 markdown 代码块,只输出 JSON

### 例子
输入: "慕尼黑中央火车站"
输出: {"intent_zh":"慕尼黑中央火车站(主火车站)","intent_de":"Münchens Hauptbahnhof","search_queries":["München Hauptbahnhof","Hauptbahnhof","München Hbf"],"rationale":"中文'中央火车站'对应 Hauptbahnhof,城市前缀加在最完整 query 里"}

输入: "圣母教堂"
输出: {"intent_zh":"慕尼黑圣母教堂(Frauenkirche)","intent_de":"Frauenkirche in München","search_queries":["Frauenkirche","München Frauenkirche"],"rationale":"圣母教堂是 Frauenkirche 标准名,OSM 里也是这个"}

输入: "BMW Welt"
输出: {"intent_zh":"BMW 世界(BMW 体验/展示中心)","intent_de":"BMW Welt","search_queries":["BMW Welt"],"rationale":"品牌专名不翻译"}
"""


async def _llm_plan_search_queries(user_query: str) -> dict:
    """让 LLM 把用户 query 转成 1-3 个德语搜索关键词"""
    try:
        result = generate_text(
            prompt=f"用户输入: {user_query}",
            system_prompt=AGENT_RESOLVE_SYSTEM,
            model=LLM_MODEL_DEFAULT,
            temperature=0.2,
            max_tokens=400,
        )
        data = _parse_llm_json(result["text"])
        # 兜底: 字段缺失用空
        return {
            "intent_zh": data.get("intent_zh", user_query),
            "intent_de": data.get("intent_de", user_query),
            "search_queries": [q.strip() for q in data.get("search_queries", []) if q and isinstance(q, str)][:3],
            "rationale": data.get("rationale", ""),
        }
    except Exception as e:
        # LLM 失败兜底: 原 query 作为一个搜索
        return {
            "intent_zh": user_query,
            "intent_de": user_query,
            "search_queries": [user_query],
            "rationale": f"(LLM 规划失败,兜底用原 query: {e})",
        }


@router.get("/agent-resolve")
async def api_osm_agent_resolve(
    q: str = Query(..., min_length=1, description="用户输入的地名(任意语言)"),
    bbox: str = Query(None, description="lat_min,lat_max,lng_min,lng_max 逗号分隔"),
    tile_url: str = Query(None, description="PMTiles URL"),
):
    """
    LLM 驱动的 POI 反查: 用户输入地名 → LLM 规划多 query → 搜本地 PMTiles → 合并候选

    返回:
    {
      "success": True,
      "user_query": "...",
      "intent_zh": "...",  # LLM 推断的用户意图
      "intent_de": "...",
      "rationale": "...",
      "search_queries": ["query1", "query2"],  # LLM 生成的实际去搜的 query
      "candidates": [...top 5],  # 合并去重后的候选 POI
      "per_query": { "query1": {"best_match":..., "count":N}, ... }  # 每个 query 的最佳结果(用于调试/展示)
    }
    """
    if bbox:
        try:
            parts = [float(x.strip()) for x in bbox.split(",")]
            if len(parts) != 4:
                raise ValueError
            lat_min, lat_max, lng_min, lng_max = parts
        except ValueError:
            raise HTTPException(status_code=400, detail="bbox 必须是 'lat_min,lat_max,lng_min,lng_max'")
    else:
        lat_min, lat_max, lng_min, lng_max = 48.06, 48.25, 11.36, 11.75

    # Step 1: LLM 规划搜索 query
    plan = await _llm_plan_search_queries(q)
    queries_to_try = plan["search_queries"] or [q]

    # Step 2: 跑每个 query 的 PMTiles 搜索
    seen_keys = set()
    all_results = []
    per_query = {}

    for query in queries_to_try:
        try:
            data = geocode_osm_poi(
                query=query,
                lat_min=lat_min, lat_max=lat_max,
                lng_min=lng_min, lng_max=lng_max,
                tile_url=tile_url,
                timeout=20,
            )
        except Exception as e:
            per_query[query] = {"error": str(e)}
            continue

        if not data.get("success"):
            per_query[query] = {"error": data.get("error", "unknown")}
            continue

        # 记录每个 query 的 best_match
        per_query[query] = {
            "best_match": data.get("best_match"),
            "count": len(data.get("results", [])),
        }

        for r in data.get("results", []):
            key = f"{r['lat']:.5f}_{r['lng']:.5f}"
            if key in seen_keys:
                continue
            seen_keys.add(key)
            r["_matched_query"] = query
            all_results.append(r)

    # Step 3: 全局合并 + 排序,取 top 5
    all_results.sort(key=lambda x: x.get("combined_score", 0), reverse=True)
    top_candidates = all_results[:5]

    # Step 4: 推荐 best(若没有 best_match,从 top 取第一个)
    recommended = None
    for q in queries_to_try:
        b = per_query.get(q, {}).get("best_match")
        if b:
            recommended = b
            recommended["_matched_query"] = q
            break
    if not recommended and top_candidates:
        recommended = top_candidates[0]

    return {
        "success": True,
        "user_query": q,
        "intent_zh": plan["intent_zh"],
        "intent_de": plan["intent_de"],
        "rationale": plan["rationale"],
        "search_queries": queries_to_try,
        "recommended": recommended,
        "candidates": top_candidates,
        "per_query": per_query,
    }


# ── 兼容旧端点 /api/osm/geocode — 但不再 LLM 翻译,只跑单个 query ──
@router.get("/geocode")
async def api_osm_geocode(
    q: str = Query(..., min_length=1),
    bbox: str = Query(None),
    tile_url: str = Query(None),
):
    """简单版: 单 query 搜 PMTiles(不调 LLM)"""
    if bbox:
        parts = [float(x.strip()) for x in bbox.split(",")]
        if len(parts) != 4:
            raise HTTPException(status_code=400, detail="bbox 必须是 'lat_min,lat_max,lng_min,lng_max'")
        lat_min, lat_max, lng_min, lng_max = parts
    else:
        lat_min, lat_max, lng_min, lng_max = 48.06, 48.25, 11.36, 11.75

    data = geocode_osm_poi(
        query=q,
        lat_min=lat_min, lat_max=lat_max,
        lng_min=lng_min, lng_max=lng_max,
        tile_url=tile_url,
    )
    return data
