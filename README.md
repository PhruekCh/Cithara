# Cithara – AI Music Generation Platform

## Setup
```bash
python -m venv venv && source venv/bin/activate   # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                               # edit .env with your settings
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

CRUD test: http://127.0.0.1:8000/api/creators/

---

## Song Generation (Strategy Pattern)

Cithara uses the **Strategy design pattern** to support interchangeable song-generation behaviors.
The active strategy is selected via a single environment variable — no code changes needed.

### Quick Demonstration

You can quickly run a complete standalone demonstration of both modes without needing to start the Django server or use `curl`:

```bash
# Run Mock mode demonstration
python demo_generation.py mock

# Run Suno mode demonstration (requires SUNO_API_KEY in .env)
python demo_generation.py suno
```
(See `demo_output.md` for example output).

### Architecture

```
GenerateSongView
       │
       ▼
 get_generator()          ← reads GENERATOR_STRATEGY setting
       │
       ├── MockSongGeneratorStrategy    (offline, deterministic)
       └── SunoSongGeneratorStrategy    (calls Suno API)
```

All strategies implement the same interface (`SongGeneratorStrategy`):
- `generate(request)` → submit a generation job
- `check_status(task_id)` → poll for results

### Configuration

Copy the example env file and edit it:

```bash
cp .env.example .env
```

`.env` contents:
```env
# 'mock' (default, offline) or 'suno' (real API)
GENERATOR_STRATEGY=mock

# Required only when GENERATOR_STRATEGY=suno
SUNO_API_KEY=your_suno_api_key_here
```

> **⚠️ Never commit your `.env` file.** It is already in `.gitignore`.

### Running in Mock Mode (default)

Set `GENERATOR_STRATEGY=mock` (or omit it entirely):

```bash
python manage.py runserver
```

Test generation:
```bash
curl -X POST http://127.0.0.1:8000/api/generate/ \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "A calm piano melody about rain",
       "style": "Classical",
       "title": "Rainy Day",
       "genre": "jazz",
       "mood": "calm",
       "occasion": "relaxation",
       "library": 1
     }'
```

Mock mode returns `SUCCESS` immediately with placeholder audio URLs.

### Running in Suno Mode

1. Get an API key from https://sunoapi.org/api-key
2. Set your `.env`:
   ```env
   GENERATOR_STRATEGY=suno
   SUNO_API_KEY=your_real_key_here
   ```
3. Restart the server
4. Generate a song (same curl as above)
5. The response will contain a `task_id` with status `PENDING`
6. Poll for results:
   ```bash
   curl http://127.0.0.1:8000/api/generate/<task_id>/status/
   ```
   Status progresses: `PENDING` → `TEXT_SUCCESS` → `FIRST_SUCCESS` → `SUCCESS`

### API Endpoints

| Endpoint                             | Method | Description                            |
| ------------------------------------ | ------ | -------------------------------------- |
| `/api/generate/`                     | POST   | Submit a song generation request       |
| `/api/generate/<task_id>/status/`    | GET    | Poll generation status and get results |
| `/api/songs/`                        | GET    | List all songs (CRUD)                  |
| `/api/creators/`                     | GET    | List all creators (CRUD)               |
| `/api/libraries/`                    | GET    | List all libraries (CRUD)              |
| `/api/listeners/`                    | GET    | List all listeners (CRUD)              |

### Usage Example: Creating a Library

To use the `/api/generate/` endpoint, you must first have a `Library` to store the generated songs. Because a `Library` has a 1-to-1 relationship with a `Creator`, you must pass an existing creator's ID.

> **⚠️ Windows (PowerShell):** JSON values inside double-quoted strings must use `\"` escaped quotes.

**Windows (PowerShell):**
```powershell
# 1. Create a Creator
curl -X POST http://127.0.0.1:8000/api/creators/ -H "Content-Type: application/json" -d "{\"email\": \"mozart@example.com\", \"display_name\": \"Mozart\"}"

# 2. Create the Library (use the id returned above, e.g. 1)
curl -X POST http://127.0.0.1:8000/api/libraries/ -H "Content-Type: application/json" -d "{\"creator\": 1}"
```

**Linux / macOS (bash):**
```bash
# 1. Create a Creator
curl -X POST http://127.0.0.1:8000/api/creators/ \
     -H "Content-Type: application/json" \
     -d '{"email": "mozart@example.com", "display_name": "Mozart"}'

# 2. Create the Library (use the id returned above, e.g. 1)
curl -X POST http://127.0.0.1:8000/api/libraries/ \
     -H "Content-Type: application/json" \
     -d '{"creator": 1}'
```

### Where to Put the Suno API Key

- Store it in the `.env` file at the project root (never committed)
- Or set it as an OS environment variable: `export SUNO_API_KEY=...`
- The key is read by Django settings and used by `SunoSongGeneratorStrategy`
