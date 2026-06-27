"""用新 GOOGLE_API_KEY 测 Google Cloud TTS (Standard 音色) + 词级时间戳"""
import os
import sys
import urllib.request
import urllib.error
import json
import base64

# 读新 key (从 vault secrets.env)
vault_path = '/Volumes/NewDisk/.agent-secrets/secrets.env'
key = None
if os.path.exists(vault_path):
    with open(vault_path) as f:
        for line in f:
            if line.startswith('export GOOGLE_API_KEY='):
                key = line.split('=', 1)[1].strip().strip('"').strip("'")
                break
print(f'using key: {key[:20]}...')

# Test 1: TTS with Standard voice + timepoints
print()
print('=== Test 1: de-DE-Standard-A (女声) + SSML_MARK timepoints ===')
url = f'https://texttospeech.googleapis.com/v1/text:synthesize?key={key}'
body = json.dumps({
    "input": {"text": "Guten Tag, mein Name ist Hans. Ich komme aus München."},
    "voice": {"languageCode": "de-DE", "name": "de-DE-Standard-A"},
    "audioConfig": {
        "audioEncoding": "MP3",
        "enableTimePointing": ["SSML_MARK"]
    }
}).encode('utf-8')
req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'}, method='POST')
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.loads(r.read())
        audio_b64 = d.get('audioContent', '')
        audio_bytes = base64.b64decode(audio_b64)
        timepoints = d.get('timepoints', [])
        print(f'  audio: {len(audio_bytes)} bytes')
        print(f'  timepoints: {len(timepoints)}')
        for tp in timepoints[:8]:
            mark = tp.get('markName', '?')
            secs = tp.get('timeSeconds', '?')
            nsecs = tp.get('timeNanos', 0)
            total_secs = secs + nsecs / 1e9 if isinstance(secs, (int, float)) else nsecs / 1e9
            print(f'    {total_secs:.3f}s  mark={mark!r}')
except urllib.error.HTTPError as e:
    err = e.read().decode()[:500]
    print(f'  HTTP {e.code}: {err}')

# Test 2: 中文 Standard
print()
print('=== Test 2: zh-CN-Standard-A + SSML_MARK ===')
body = json.dumps({
    "input": {"text": "玛利亚广场是德国慕尼黑市中心的一座广场,形成于1158年。"},
    "voice": {"languageCode": "zh-CN", "name": "zh-CN-Standard-A"},
    "audioConfig": {
        "audioEncoding": "MP3",
        "enableTimePointing": ["SSML_MARK"]
    }
}).encode('utf-8')
req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'}, method='POST')
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.loads(r.read())
        audio_bytes = base64.b64decode(d.get('audioContent', ''))
        timepoints = d.get('timepoints', [])
        print(f'  audio: {len(audio_bytes)} bytes, timepoints: {len(timepoints)}')
        for tp in timepoints[:5]:
            nsecs = tp.get('timeNanos', 0)
            print(f'    {nsecs/1e9:.3f}s  mark={tp.get("markName", "?")!r}')
except urllib.error.HTTPError as e:
    err = e.read().decode()[:300]
    print(f'  HTTP {e.code}: {err}')
