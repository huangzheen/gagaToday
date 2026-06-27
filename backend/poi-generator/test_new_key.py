"""查新 GOOGLE_API_KEY 是什么 project + 启用的服务"""
import os
import urllib.request
import urllib.error
import json

key = 'AIzaSyD4gDZ1UZM9oDrtiEIOgcXhL4nxk-Bjm6U'

# 1. 用 Gemini API 拿到 project_id
print('=== Project ID ===')
url = f'https://generativelanguage.googleapis.com/v1beta/models?key={key}'
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        d = json.loads(r.read())
        for m in d.get('models', [])[:3]:
            print(f'  {m.get("name")}')
        # project ID 没法直接看
except Exception as e:
    print(f'  ERR: {e}')

# 2. 试开 TTS API
print()
print('=== 试图 enable texttospeech ===')
url = f'https://serviceusage.googleapis.com/v1/services/texttospeech.googleapis.com:enable?key={key}'
req = urllib.request.Request(url, data=b'{}', headers={'Content-Type': 'application/json'}, method='POST')
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print(f'  enable result: {d}')
except urllib.error.HTTPError as e:
    err = e.read().decode()[:500]
    print(f'  HTTP {e.code}: {err}')

# 3. 试 texttospeech 直接
print()
print('=== 直接调 texttospeech ===')
url = f'https://texttospeech.googleapis.com/v1/voices?key={key}'
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        d = json.loads(r.read())
        print(f'  voices count: {len(d.get("voices", []))}')
        # 找几个 de 的
        for v in d.get('voices', [])[:3]:
            print(f'    {v.get("name")} ({v.get("languageCodes")})')
except urllib.error.HTTPError as e:
    err = e.read().decode()[:500]
    print(f'  HTTP {e.code}: {err}')
