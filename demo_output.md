# Minimal Demonstration — Strategy Pattern Output

## How to reproduce

```bash
# Mock mode (no API key needed)
python demo_generation.py mock

# Suno mode (requires SUNO_API_KEY in .env)
python demo_generation.py suno
```

---

## Strategy A — Mock Generation

**Command:**
```
python demo_generation.py mock
```

**Output:**
```
============================================================
  STRATEGY A - Mock (Offline / Deterministic)
============================================================

[1] Calling MockSongGeneratorStrategy.generate() ...

{
  "task_id": "8eac9745-3c87-4a53-8e09-0bf4d9941721",
  "status": "SUCCESS",
  "data": {
    "sunoData": [
      {
        "id": "c1388f2f-a0bd-443f-97e3-d3ed31f2b9b4",
        "audioUrl": "https://example.com/mock-audio.mp3",
        "streamAudioUrl": "https://example.com/mock-stream",
        "imageUrl": "https://example.com/mock-cover.jpeg",
        "prompt": "A calm piano melody about rain and nostalgia",
        "title": "Rainy Memories",
        "tags": "Classical",
        "duration": 180.0
      }
    ]
  }
}

[2] Calling check_status(task_id='8eac9745-3c87-4a53-8e09-0bf4d9941721') ...

{
  "task_id": "8eac9745-3c87-4a53-8e09-0bf4d9941721",
  "status": "SUCCESS",
  "data": {
    "sunoData": [
      {
        "id": "c1388f2f-a0bd-443f-97e3-d3ed31f2b9b4",
        "audioUrl": "https://example.com/mock-audio.mp3",
        "streamAudioUrl": "https://example.com/mock-stream",
        "imageUrl": "https://example.com/mock-cover.jpeg",
        "prompt": "A calm piano melody about rain and nostalgia",
        "title": "Rainy Memories",
        "tags": "Classical",
        "duration": 180.0
      }
    ]
  }
}

[OK] Mock strategy works - returned SUCCESS immediately with placeholder URLs.
```

**Result:** Mock strategy returns `SUCCESS` immediately with a `task_id`, placeholder `audioUrl`, `imageUrl`, and `duration`. No network access needed.

---

## Strategy B — Suno API Generation (Real)

**Command:**
```
python demo_generation.py suno
```

**Output:**
```
============================================================
  STRATEGY B - Suno API (Real AI Generation)
============================================================

  API key: 0f51d0a7****fd8b

[1] Calling SunoSongGeneratorStrategy.generate() ...

{
  "task_id": "0a9923e3d528bfeffcef3dfbf5c8fdbb",
  "status": "PENDING",
  "data": null
}

[2] Calling check_status(task_id='0a9923e3d528bfeffcef3dfbf5c8fdbb') ...

{
  "task_id": "0a9923e3d528bfeffcef3dfbf5c8fdbb",
  "status": "PENDING",
  "data": null,
  "error_message": null
}

[OK] Suno strategy works - taskId '0a9923e3d528bfeffcef3dfbf5c8fdbb' created, status: PENDING.
     Keep polling GET /api/generate/<task_id>/status/ until status == SUCCESS.
```

**Result:**
- `POST /api/v1/generate` → Suno accepted the request and returned `taskId: 0a9923e3d528bfeffcef3dfbf5c8fdbb`
- `GET /api/v1/generate/record-info?taskId=...` → status is `PENDING` (Suno is generating the song)
- Status will progress: `PENDING` → `TEXT_SUCCESS` → `FIRST_SUCCESS` → `SUCCESS`
- Once `SUCCESS`, the response will contain real audio URLs from the Suno CDN

---

## Raw Suno API Response (from debug run)

**POST /generate response:**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "taskId": "09c0edbd9dc50df9b6174a7b240bbcba"
  }
}
```

**GET /generate/record-info response:**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "taskId": "09c0edbd9dc50df9b6174a7b240bbcba",
    "parentMusicId": "",
    "param": "{\"callBackUrl\":\"https://httpbin.org/post\",\"customMode\":true,\"instrumental\":false,\"model\":\"V4\",\"prompt\":\"A calm piano melody about rain\",\"style\":\"Classical\",\"title\":\"Rainy Memories\"}",
    "response": null,
    "status": "PENDING",
    "type": "chirp-v4",
    "operationType": "generate",
    "errorCode": null,
    "errorMessage": null,
    "createTime": 1776340072000
  }
}
```
