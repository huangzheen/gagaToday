"""
Wiki / Web Search — 场景介绍抓取编排
"""

import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.wiki_service import fetch_intro
from ..config import BRAVE_API_KEY

router = APIRouter(prefix="/api/wiki", tags=["wiki"])


class WikiIntroRequest(BaseModel):
    name_de: str
    name_zh: str = None
    name_en: str = None


@router.post("/intro")
async def api_wiki_intro(req: WikiIntroRequest):
    """
    抓取地点三语场景介绍

    流程: Wikipedia DE → Wikidata 跨语言 → Brave Search fallback → LLM 改写/翻译
    """
    if not req.name_de:
        raise HTTPException(status_code=400, detail="name_de is required")
    try:
        result = fetch_intro(req.name_de, req.name_zh, req.name_en)
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── 临时: CosyVoice 词级时间戳能力测试 ──
@router.get("/test-tts-words")
async def test_tts_words():
    """用 streaming call 测 CosyVoice v1 能否给词级时间戳"""
    import dashscope
    from dashscope.audio.tts_v2 import SpeechSynthesizer, ResultCallback
    from dashscope.audio.tts_v2.speech_synthesizer import AudioFormat
    from ..config import DASHSCOPE_API_KEY

    dashscope.api_key = DASHSCOPE_API_KEY

    words = []
    audio_size = [0]
    all_events = []

    class Cb(ResultCallback):
        def on_word(self, m):
            words.append(dict(m))
            all_events.append(("word", m))
        def on_data(self, data):
            audio_size[0] += len(data) if data else 0
        def on_error(self, m):
            print(f'[test_tts_words] on_error: {m}')
        def on_close(self):
            print(f'[test_tts_words] on_close, events: {len(all_events)}')
        def on_event(self, message):
            # catch-all 看 SDK 还提供什么事件
            all_events.append(("event", message))

    s = SpeechSynthesizer(
        model="cosyvoice-v1",
        voice="longxiaocheng",
        format=AudioFormat.MP3_22050HZ_MONO_256KBPS,
        callback=Cb(),
        instruction="rate=1.0; pitch=0; word_timestamp=true",  # 试图开词级时间戳
    )
    s.streaming_call("Guten Tag mein Name ist Hans. Ich komme aus München.")
    s.streaming_complete()
    time.sleep(3)

    # 看看 SDK 暴露的回调方法
    cb_methods = [m for m in dir(ResultCallback) if not m.startswith('_')]

    # 收集所有非空事件,解析 JSON 看里面有什么
    import json
    event_strs = []
    for ev_type, ev_msg in all_events[:5]:
        try:
            # ev_msg 可能是 JSON 字符串
            if isinstance(ev_msg, str):
                try:
                    parsed = json.loads(ev_msg)
                    # 只看 payload.output 的 keys
                    out = parsed.get('payload', {}).get('output', {})
                    if isinstance(out, dict):
                        out = {k: (f"<{len(v)} bytes>" if isinstance(v, bytes) else str(v)[:200]) for k, v in out.items()}
                    event_strs.append({"type": ev_type, "event": parsed.get('header', {}).get('event'), "output_keys": list(out.keys()) if isinstance(out, dict) else str(out)[:100], "output_sample": out})
                except Exception as je:
                    event_strs.append({"type": ev_type, "raw_str": ev_msg[:300]})
            else:
                event_strs.append({"type": ev_type, "repr": repr(ev_msg)[:200]})
        except Exception as e:
            event_strs.append({"type": ev_type, "err": str(e)})

    return {
        "success": True,
        "words_count": len(words),
        "audio_size": audio_size[0],
        "sample_words": words[:6],
        "all_events_count": len(all_events),
        "events_summary": event_strs,
        "callback_methods": cb_methods,
    }