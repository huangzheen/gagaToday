"""查 GOOGLE_API_KEY 启用的所有服务"""
import os
import urllib.request
import urllib.error
import json

key = os.environ.get('GOOGLE_API_KEY', 'AIzaSyCPm_3EIhxVWIeczOeF4PxkNI6UxN-wIzc')

# 列出 project 启用的 services
print('=== 列出 project 启用的服务 ===')
url = f'https://serviceusage.googleapis.com/v1/projects/808513433680/services?key={key}&pageSize=200'
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        d = json.loads(r.read())
        services = d.get('services', [])
        print(f'Total: {len(services)}')
        for s in services:
            name = s.get('config', {}).get('name', '?')
            state = s.get('state', '?')
            if 'tts' in name.lower() or 'speech' in name.lower() or 'translate' in name.lower() or 'language' in name.lower():
                print(f'  ★ {name} : {state}')
        # 全部列出来方便看
        print()
        print('All enabled:')
        for s in services:
            name = s.get('config', {}).get('name', '?').replace('googleapis.com/', '')
            print(f'  {s.get("state"):8s} {name}')
except urllib.error.HTTPError as e:
    err = e.read().decode()[:500]
    print(f'HTTP {e.code}: {err}')

# 同时看这个 key 绑定的 project 的元信息
print()
print('=== 查 project 的元信息 ===')
# 没法直接看,但可以试一些常见的测试
for test_url, name in [
    (f'https://generativelanguage.googleapis.com/v1beta/models?key={key}', 'Gemini API'),
    (f'https://translation.googleapis.com/language/translate/v2?key={key}&q=hello&target=de', 'Cloud Translation'),
]:
    try:
        with urllib.request.urlopen(test_url, timeout=5) as r:
            d = json.loads(r.read())
            print(f'  {name}: OK (response keys: {list(d.keys())[:5]})')
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:200]
        print(f'  {name}: HTTP {e.code}: {err[:150]}')
    except Exception as e:
        print(f'  {name}: ERR: {e}')
