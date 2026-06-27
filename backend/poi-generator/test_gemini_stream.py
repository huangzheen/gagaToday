"""测 Gemini TTS 流式 (WebSocket/streaming) 有没有 word timestamps"""
import os
import urllib.request
import json
import base64

key = os.environ.get('GOOGLE_API_KEY', 'AIzaSyCPm_3EIhxVWIeczOeF4PxkNI6UxN-wIzc')

# Gemini API 支持 streamGenerateContent (SSE)
print('=== Gemini TTS streaming (SSE) ===')
url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:streamGenerateContent?key={key}&alt=sse'
body = json.dumps({
    "contents": [{
        "parts": [{"text": "Guten Tag mein Name ist Hans"}]
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
        # 流式: 读 SSE
        chunk_count = 0
        total_audio = 0
        events = []
        for line in r:
            line = line.decode('utf-8', errors='ignore').strip()
            if not line or not line.startswith('data: '): continue
            data = line[6:]
            if data == '[DONE]': break
            try:
                d = json.loads(data)
                chunk_count += 1
                # 找音频
                for cand in d.get('candidates', []):
                    for part in cand.get('content', {}).get('parts', []):
                        inline = part.get('inlineData') or part.get('inline_data')
                        if inline and 'data' in inline:
                            total_audio += len(base64.b64decode(inline['data']))
                # 记录事件类型
                if chunk_count <= 3:
                    events.append(json.dumps(d)[:300])
            except Exception:
                pass
        print(f'  chunks: {chunk_count}, total audio bytes: {total_audio}')
        for e in events:
            print(f'  {e}')
except urllib.error.HTTPError as e:
    err = e.read().decode()[:500]
    print(f'  HTTP {e.code}: {err}')
