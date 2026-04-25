# Sequence Diagram — Song Generation Use Case (UC-02)

## Overview
This document presents the **sequence diagram** for the core "Generate & Collect Music" use case (UC-02) of the Cithara platform. It shows the interaction flow between the Creator, the browser UI (Template), the Django backend (View), the data models, and the external Suno AI API.

## Sequence Diagram

```mermaid
sequenceDiagram
    actor Creator
    participant Browser as Browser/Template<br>(studio.html)
    participant View as GenerateSongView<br>(View Layer)
    participant Factory as get_generator()<br>(Strategy Factory)
    participant Strategy as SongGeneratorStrategy<br>(Strategy Interface)
    participant SunoAPI as Suno API<br>(External Service)
    participant SongModel as Song<br>(Model)
    participant JobModel as GenerationJob<br>(Model)
    participant StatusView as GenerationStatusView<br>(View Layer)

    Note over Creator, StatusView: UC-02: Generate & Collect Music

    Creator->>Browser: Fill in Prompt, Title, Genre, Mood, Occasion, Style
    Creator->>Browser: Click "Generate Song"

    Browser->>Browser: Validate input (< 1000 chars)
    Browser->>View: POST /api/generate/<br>{prompt, title, genre, mood, occasion, style, library}

    View->>View: Validate via GenerationRequestSerializer
    View->>SongModel: Song.objects.create(library, title, genre, mood, occasion)
    SongModel-->>View: song instance

    View->>Factory: get_generator()
    Factory->>Factory: Check GENERATOR_STRATEGY setting
    alt strategy == 'suno'
        Factory-->>View: SunoSongGeneratorStrategy instance
    else strategy == 'mock'
        Factory-->>View: MockSongGeneratorStrategy instance
    end

    View->>Strategy: generate({prompt, style, title})

    alt Suno Strategy
        Strategy->>SunoAPI: POST /api/v1/generate<br>{prompt, style, title, model: "V4"}
        SunoAPI-->>Strategy: {taskId, status: "PENDING"}
        Strategy-->>View: {task_id, status: "PENDING"}
    else Mock Strategy
        Strategy-->>View: {task_id, status: "SUCCESS", data: {sunoData: [...]}}
    end

    View->>JobModel: GenerationJob.objects.create(song, task_id, status, strategy_used)
    JobModel-->>View: job instance

    alt Immediate SUCCESS (Mock)
        View->>SongModel: Update audio_url, duration
        View-->>Browser: 201 {job data, status: "SUCCESS"}
        Browser->>Browser: showPreview() — show "Generation Complete" card
        Browser->>Creator: Display success toast + link to Library/Song
    else PENDING (Suno — async)
        View-->>Browser: 201 {job data, status: "PENDING"}
        Browser->>Browser: showProgress("PENDING") — start progress bar + timer

        loop Poll every 3 seconds (max 15 min)
            Browser->>StatusView: GET /api/generate/{task_id}/status/
            StatusView->>JobModel: GenerationJob.objects.get(task_id)
            StatusView->>Strategy: check_status(task_id)
            Strategy->>SunoAPI: GET /api/v1/generate/record-info?taskId={task_id}
            SunoAPI-->>Strategy: {status, response: {sunoData}}
            Strategy-->>StatusView: {task_id, status, data}

            alt status == "SUCCESS"
                StatusView->>JobModel: Update audio_url, stream_audio_url, image_url
                StatusView->>SongModel: Update audio_url, duration
                StatusView-->>Browser: {status: "SUCCESS", audio_url, ...}
                Browser->>Browser: showProgress("SUCCESS") + showPreview()
                Browser->>Creator: Display success toast
            else status == "TEXT_SUCCESS" or "FIRST_SUCCESS"
                StatusView-->>Browser: {status: "TEXT_SUCCESS/FIRST_SUCCESS"}
                Browser->>Browser: Update progress bar (40%/70%)
            else status == "FAILED"
                StatusView->>JobModel: Update error_message
                StatusView-->>Browser: {status: "FAILED", error_message}
                Browser->>Browser: showProgress("FAILED")
                Browser->>Creator: Display error toast
            else Timeout (15 min)
                Browser->>Browser: Abort polling
                Browser->>Creator: Display timeout toast (FR-06)
            end
        end
    end
```

## Actors and Components

| Component | Layer | Description |
|---|---|---|
| Creator | Actor | The authenticated user generating music |
| Browser/Template | Template (MVT) | `studio.html` + `app.js` — handles form, progress bar, polling |
| GenerateSongView | View (MVT) | Handles POST `/api/generate/` — creates Song + delegates to strategy |
| GenerationStatusView | View (MVT) | Handles GET `/api/generate/{task_id}/status/` — polls strategy |
| get_generator() | Strategy Factory | Returns the active strategy based on `GENERATOR_STRATEGY` setting |
| SongGeneratorStrategy | Strategy Interface | Abstract base class defining `generate()` and `check_status()` |
| Suno API | External Service | Third-party AI music generation API |
| Song | Model (MVT) | The core artifact — stores metadata and audio URL |
| GenerationJob | Model (MVT) | Tracks async generation task status and results |

## Key Design Decisions

1. **Strategy Pattern**: The generation logic is decoupled via `SongGeneratorStrategy`. This allows seamless switching between `MockSongGeneratorStrategy` (offline dev) and `SunoSongGeneratorStrategy` (production) via a single environment variable.

2. **Asynchronous Polling**: Since Suno API generation is async (can take minutes), the frontend polls `/api/generate/{task_id}/status/` every 3 seconds with a 15-minute timeout (FR-06).

3. **Progressive Status**: The system tracks 4 status stages: `PENDING` → `TEXT_SUCCESS` → `FIRST_SUCCESS` → `SUCCESS`, providing granular progress feedback to the user.
