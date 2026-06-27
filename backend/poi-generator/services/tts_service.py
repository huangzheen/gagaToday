"""
TTS (Text-to-Speech) 服务 — CosyVoice 封装 (Aliyun DashScope)

- 场景介绍文本 → MP3 音频
- 预生成 + 缓存到 assets/scenes/<city>/<poi_id>/audio/intro_<lang>.mp3
- 选型依据: archive/docs/API_STACK.md
- DashScope Python SDK: pip install dashscope
- 新用户福利: 180 天 100 万 token 免费额度
- 实测可用 model: cosyvoice-v1(v2/v3.5 当前 API key 不支持,报 418)
"""

import os
import re
import time
from pathlib import Path
from typing import Optional

from ..config import DASHSCOPE_API_KEY


# ── 配置 ──

# CosyVoice 3.5 Plus 音色选择
# - CosyVoice 多语言模型自动检测语种,不需要为不同语言切换音色
# - longxiaocheng: 通用男声(预置官方音色,中文/英文/多语言都可用)
# - 后续可上传 10-20s 德语参考音频克隆更地道的德语男声/女声
DEFAULT_VOICE = os.environ.get("COSYVOICE_VOICE", "longxiaocheng")

# 场景介绍场景下,文本超长会超 token / 超时。CosyVoice 3.5 Plus 单次上限 ~2000 字
# 维基百科 intro 通常 500-1500 字,基本在范围内;超过时做截断
TTS_MAX_CHARS = 2000


# ── 主入口 ──


def synthesize_intro(poi_id: str, lang: str, text: str, city: str = "munich") -> Optional[dict]:
    """
    生成 POI 场景介绍的 MP3 音频文件(同步,可能耗时 2-5s)

    Args:
        poi_id: 'marienplatz' / 'frauenkirche'
        lang: 'de' | 'zh' | 'en'
        text: 场景介绍文本(任意长度,内部会截断到 TTS_MAX_CHARS)
        city: 城市目录(默认 munich)

    Returns:
        {
            "path": "/abs/path/to/intro_de.mp3",
            "url": "/assets/scenes/munich/marienplatz/audio/intro_de.mp3",
            "size_bytes": 12345,
            "duration_estimate": 8.5,  # 秒
        }
        或 None(失败)
    """
    if not text or not text.strip():
        return None
    if lang not in ("de", "zh", "en"):
        raise ValueError(f"unsupported lang: {lang}")

    # 路径: assets/scenes/<city>/<poi_id>/audio/intro_<lang>.mp3
    project_root = Path(__file__).resolve().parents[3]  # backend/poi-generator/services/tts_service.py → 3 级回根
    audio_dir = project_root / "assets" / "scenes" / city / poi_id / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    target = audio_dir / f"intro_{lang}.mp3"

    # 截断超长文本(优先在句末切,避免 TTS 念到一半)
    truncated = _truncate_for_tts(text, TTS_MAX_CHARS)

    # 调 CosyVoice
    try:
        mp3_bytes = _call_cosyvoice(truncated)
    except Exception as e:
        print(f"[tts_service] CosyVoice 失败 ({poi_id}/{lang}): {e}")
        return None

    if not mp3_bytes or len(mp3_bytes) < 100:
        print(f"[tts_service] CosyVoice 返回内容异常 ({poi_id}/{lang}): {len(mp3_bytes) if mp3_bytes else 0} bytes")
        return None

    # 落盘
    target.write_bytes(mp3_bytes)

    # 估算时长(德语/英语 ~150 词/分钟,中文 ~200 字/分钟)
    if lang == "zh":
        # 中文字符数,语速约 200 字/分钟
        chars = len(re.sub(r"\s+", "", truncated))
        duration_s = chars / (200 / 60)
    else:
        # 词数,语速约 150 词/分钟
        words = len(truncated.split())
        duration_s = words / (150 / 60)

    return {
        "path": str(target),
        "url": f"/assets/scenes/{city}/{poi_id}/audio/intro_{lang}.mp3",
        "size_bytes": len(mp3_bytes),
        "duration_estimate": round(duration_s, 1),
    }


# ── 内部 helpers ──


def _call_cosyvoice(text: str, max_retries: int = 2) -> bytes:
    """
    调 CosyVoice 同步合成 → 返回 MP3 bytes
    失败时自动重试,带指数退避

    实测可用: cosyvoice-v1 + longxiaocheng(v2/v3.5 当前 API key 不支持)
    """
    import dashscope
    from dashscope.audio.tts_v2 import SpeechSynthesizer
    from dashscope.audio.tts_v2.speech_synthesizer import AudioFormat

    dashscope.api_key = DASHSCOPE_API_KEY

    last_err = None
    for attempt in range(max_retries + 1):
        try:
            synthesizer = SpeechSynthesizer(
                model="cosyvoice-v1",  # 当前 API key 唯一可用模型
                voice=DEFAULT_VOICE,
                format=AudioFormat.MP3_22050HZ_MONO_256KBPS,  # 22kHz mono,256kbps MP3(语音最佳平衡)
            )
            audio_bytes = synthesizer.call(text)
            if not audio_bytes:
                raise RuntimeError("CosyVoice 返回空音频")
            return audio_bytes
        except Exception as e:
            last_err = e
            if attempt < max_retries:
                wait_s = 2 ** attempt
                print(f"[tts_service] CosyVoice 重试 (attempt {attempt+1}/{max_retries}), 等待 {wait_s}s: {e}")
                time.sleep(wait_s)
    raise RuntimeError(f"CosyVoice 3 次尝试均失败: {last_err}")


def _truncate_for_tts(text: str, max_chars: int) -> str:
    """截断到 max_chars,优先在句末(。.!?)切,避免 TTS 念半句"""
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    for sep in ["\n\n", "。", "!\n", "! ", ".\n", ". ", "？", "?\n", "? "]:
        idx = cut.rfind(sep)
        if idx > max_chars * 0.7:  # 至少保留 70%
            return cut[: idx + (1 if sep in "。!?" else len(sep))].strip()
    return cut.strip() + "..."
