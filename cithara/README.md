# Cithara — AI Music Generation Platform

Cithara is a Django-based web application that lets users generate AI-powered music using the **Suno API**. It features a Strategy pattern for swappable generation backends, Google OAuth authentication, and a personal music library.

## Prerequisites

- Python 3.12+
- pip

## Quick Start

### 1. Clone & Install

```bash
git clone <repo-url>
cd Cithara

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with the following settings:

```env
# Song generation strategy: 'mock' (offline/testing) or 'suno' (real API)
GENERATOR_STRATEGY=mock

# Required only when GENERATOR_STRATEGY=suno
SUNO_API_KEY=your_suno_api_key_here

# Google OAuth 2.0 credentials (see setup instructions below)
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

### 3. Google OAuth Setup

To enable "Sign in with Google":

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Navigate to **APIs & Services → Credentials**
4. Click **Create Credentials → OAuth client ID**
5. Select **Web application** as the application type
6. Under **Authorized redirect URIs**, add:
   ```
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```
   (Also add `http://localhost:8000/accounts/google/login/callback/` if needed)
7. Copy the **Client ID** and **Client Secret** into your `.env` file

> **Note:** If you only want to test with local username/password registration (no Google login), you can leave the `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` values empty. The local registration at `/register/` will still work.

### 4. Run Migrations & Start Server

```bash
python manage.py migrate
python manage.py runserver
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) to access the app.

## Usage

| Feature | URL |
|---|---|
| Login | `/login/` |
| Register (local) | `/register/` |
| Google OAuth Login | `/accounts/google/login/` |
| Music Library | `/library/` |
| Creation Studio | `/studio/` |
| Song Detail | `/song/<id>/` |
| REST API (Songs) | `/api/songs/` |

## Generation Strategies

Cithara uses the **Strategy design pattern** to swap between generation backends:

| Strategy | `GENERATOR_STRATEGY` | Description |
|---|---|---|
| **Mock** | `mock` | Offline, instant, returns placeholder data. Ideal for development & testing. |
| **Suno API** | `suno` | Calls the real [Suno API](https://sunoapi.org/) to generate AI music. Requires a valid `SUNO_API_KEY`. |

Change the strategy by updating the `GENERATOR_STRATEGY` value in your `.env` file and restarting the server.

## Project Structure

```
Cithara/
├── cithara/             # Django project settings & URL config
├── domain/
│   ├── generation/      # Strategy pattern (mock + suno strategies)
│   ├── models/          # Song, Library, GenerationJob, Creator, Listener
│   ├── serializers/     # DRF serializers
│   ├── views/           # API views + frontend views
│   ├── templates/       # HTML templates (MVT)
│   └── static/          # CSS, JS, images
├── docs/                # Domain model, class diagram, sequence diagram
├── .env.example         # Environment variable template
├── requirements.txt     # Python dependencies
└── manage.py
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/songs/` | List all songs |
| POST | `/api/songs/` | Create a song |
| GET | `/api/songs/<id>/` | Retrieve a song |
| PATCH | `/api/songs/<id>/` | Update a song (e.g. rating) |
| DELETE | `/api/songs/<id>/` | Soft-delete a song |
| POST | `/api/generate/` | Start song generation |
| GET | `/api/generate/<task_id>/status/` | Poll generation status |
