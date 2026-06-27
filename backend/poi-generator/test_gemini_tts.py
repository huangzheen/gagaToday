"""测 Gemini 的 TTS 能力 (gemini-2.5-flash-preview-tts)"""
import os
import urllib.request
import urllib.error
import json
import base64

key = os.environ.get('GOOGLE_API_KEY', 'AIzaSyCPm_3EIhxVWIeczOeF4PxkNI6UxN-wIzc')

print('=== Gemini 2.5 Flash TTS ===')
url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={key}'
body = {
    "contents": [{
        "parts": [{"text": "Guten Tag, mein Name ist Hans. Ich komme aus München."}]
    }],
    "generationConfig": {
        "response_modalities": ["AUDIO"],
        "speech_config": {
            "voiceConfig": {
                "prebuiltVoiceConfig": {"voiceName": "Kore"}
            }
        }
    }
}.get if False else json.dumps({
    "contents": [{
        "parts": [{"text": "Guten Tag, mein Name ist Hans. Ich komme aus München."}]
    }],
    "generationConfig": {
        "response_modalities": ["AUDIO"],
        "speech_config": {
            "voiceConfig": {
                "prebuiltVoiceConfig": {"voiceName": "Kore"}
            }
        }
    }
}).encode('utf-8')

req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'}, method='POST')
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read())
        # 找音频
        candidates = d.get('candidates', [])
        for c in candidates:
            content = c.get('content', {})
            for part in content.get('parts', []):
                inline_data = part.get('inlineData', {}) or part.get('inline_data', {})
                if inline_data:
                    mime = inline_data.get('mimeType', inline_data.get('mime_type', '?'))
                    data_b64 = inline_data.get('data', '')
                    audio_bytes = base64.b64decode(data_b64)
                    print(f'  audio mime: {mime}, bytes: {len(audio_bytes)}')
        # 看完整 response keys
        print(f'  top-level keys: {list(d.keys())}')
        if 'candidates' in d:
            c0 = d['candidates'][0]
            print(f'  candidate[0] keys: {list(c0.keys())}')
            if 'content' in c0:
                print(f'  candidate[0].content keys: {list(c0["content"].keys())}')
                for i, part in enumerate(c0['content'].get('parts', [])):
                    print(f'  part[{i}] keys: {list(part.keys())}')
                    if 'text' in part:
                        print(f'    text: {part["text"][:100]}')
        # 关键:有没有 timestamps/word timing?
        print(f'  full response (first 1000 chars):')
        print('  ' + json.dumps(d, default=str)[:1000].replace('\n', '\n  '))
except urllib.error.HTTPError as e:
    err = e.read().decode()[:500]
    print(f'  HTTP {e.code}: {err}')
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f'  ERR: {e}')
