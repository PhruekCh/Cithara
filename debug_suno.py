"""
debug_suno.py  -- check raw Suno API response
"""
import os, json, requests

API_KEY = os.environ.get("SUNO_API_KEY", "0f51d0a7c18c3abdc13cf47523a7fd8b")
BASE = "https://api.sunoapi.org/api/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "customMode": True,
    "instrumental": False,
    "model": "V4",
    "prompt": "A calm piano melody about rain and nostalgia",
    "style": "Classical",
    "title": "Rainy Memories",
}

print("[1] POST /generate")
for cb in ["https://httpbin.org/post", "https://example.com/callback", ""]:
    payload_test = {
        "customMode": True,
        "instrumental": False,
        "model": "V4",
        "prompt": "A calm piano melody about rain",
        "style": "Classical",
        "title": "Rainy Memories",
        "callBackUrl": cb,
    }
    r = requests.post(f"{BASE}/generate", headers=headers, json=payload_test, timeout=30)
    body = r.json()
    print(f"  callBackUrl={repr(cb)!r:40s} => HTTP {r.status_code}, code={body.get('code')}, msg={body.get('msg')!r}")
    if body.get("code") == 200:
        print("  FULL RESPONSE:")
        print(json.dumps(body, indent=2))
        data = body.get("data") or {}
        if isinstance(data, list):
            data = data[0] if data else {}
        task_id = data.get("taskId", "")
        print(f"  task_id: {task_id}")
        if task_id:
            print(f"\n[2] GET /generate/record-info?taskId={task_id}")
            r2 = requests.get(f"{BASE}/generate/record-info", headers=headers, params={"taskId": task_id}, timeout=30)
            print(json.dumps(r2.json(), indent=2))
        break
else:
    # Also try record-info with a known task to confirm polling works
    print("\n[2] Testing record-info endpoint with dummy taskId...")
    r2 = requests.get(f"{BASE}/generate/record-info", headers=headers, params={"taskId": "test-123"}, timeout=30)
    print(f"    HTTP {r2.status_code}")
    print(json.dumps(r2.json(), indent=2))
