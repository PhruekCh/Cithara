# Updated Class Diagram — Cithara AI Music Generation Platform

## Changelog
- **v1.2 (Updated)**:
  - Added `prompt`, `style`, `rating` attributes to `Song` class for FR-16 (Rating) and UC-08 (Regenerate)
- **v1.1 (Updated)**:
  - Added `audio_url` and `is_deleted` attributes to `Song`
  - Added `GenerationJob` class
  - Added Strategy pattern classes (`SongGeneratorStrategy`, `MockSongGeneratorStrategy`, `SunoSongGeneratorStrategy`)
  - Added Serializer classes to show full MVT architecture

---

## Class Diagram (Mermaid)

```mermaid
classDiagram
    direction TB

    %% ════════════════════════════════════════════
    %% MODEL LAYER (Domain Entities)
    %% ════════════════════════════════════════════

    class User {
        <<abstract>>
        +email : String
        +display_name : String
        +date_joined : DateTime
        +last_login : DateTime
        +__str__() String
    }

    class Creator {
        +generation_quota : Integer
        +__str__() String
    }

    class Listener {
        +recently_played : ManyToMany~Song~
        +__str__() String
    }

    class Library {
        +creator : OneToOne~Creator~
        +date_created : DateTime
        +total_songs_count() Integer
        +__str__() String
    }

    class Song {
        +library : ForeignKey~Library~
        +title : String
        +duration : Integer
        +genre : Genre
        +mood : Mood
        +occasion : Occasion
        +audio_url : URL
        +prompt : Text
        +style : String
        +rating : Integer
        +date_generated : DateTime
        +is_deleted : Boolean
        +__str__() String
    }

    class GenerationJob {
        +song : ForeignKey~Song~
        +task_id : String
        +status : Status
        +strategy_used : Strategy
        +audio_url : URL
        +stream_audio_url : URL
        +image_url : URL
        +error_message : String
        +created_at : DateTime
        +updated_at : DateTime
        +__str__() String
    }

    class Genre {
        <<enumeration>>
        ROCK
        POP
        HIPHOP
        JAZZ
        COUNTRY
    }

    class Mood {
        <<enumeration>>
        HAPPY
        SAD
        ENERGETIC
        CALM
    }

    class Occasion {
        <<enumeration>>
        WORKOUT
        FUNERAL
        CELEBRATION
        RELAXATION
    }

    %% Model Relationships
    User <|-- Creator : inherits
    User <|-- Listener : inherits
    Creator "1" -- "1" Library : owns
    Library "1" -- "*" Song : contains
    Song "1" -- "*" GenerationJob : tracked by
    Listener "*" -- "*" Song : recently_played
    Song ..> Genre : uses
    Song ..> Mood : uses
    Song ..> Occasion : uses

    %% ════════════════════════════════════════════
    %% STRATEGY PATTERN (Generation Layer)
    %% ════════════════════════════════════════════

    class SongGeneratorStrategy {
        <<abstract>>
        +generate(request : dict) dict*
        +check_status(task_id : str) dict*
    }

    class MockSongGeneratorStrategy {
        +generate(request : dict) dict
        +check_status(task_id : str) dict
    }

    class SunoSongGeneratorStrategy {
        -api_key : String
        +generate(request : dict) dict
        +check_status(task_id : str) dict
        -_headers() dict
    }

    SongGeneratorStrategy <|-- MockSongGeneratorStrategy : implements
    SongGeneratorStrategy <|-- SunoSongGeneratorStrategy : implements
    SunoSongGeneratorStrategy ..> SunoAPI : calls

    class SunoAPI {
        <<external>>
        POST /api/v1/generate
        GET /api/v1/generate/record-info
    }

    class GoogleOAuth {
        <<external>>
        OAuth 2.0 Authentication
    }

    %% ════════════════════════════════════════════
    %% VIEW LAYER (MVT)
    %% ════════════════════════════════════════════

    class CreatorViewSet {
        <<ViewSet>>
        +queryset : Creator
        +serializer_class : CreatorSerializer
    }

    class ListenerViewSet {
        <<ViewSet>>
        +queryset : Listener
        +serializer_class : ListenerSerializer
    }

    class LibraryViewSet {
        <<ViewSet>>
        +queryset : Library
        +serializer_class : LibrarySerializer
    }

    class SongViewSet {
        <<ViewSet>>
        +queryset : Song
        +serializer_class : SongSerializer
    }

    class GenerateSongView {
        <<APIView>>
        +post(request) Response
    }

    class GenerationStatusView {
        <<APIView>>
        +get(request, task_id) Response
    }

    %% View → Model relationships
    CreatorViewSet ..> Creator : manages
    ListenerViewSet ..> Listener : manages
    LibraryViewSet ..> Library : manages
    SongViewSet ..> Song : manages
    GenerateSongView ..> Song : creates
    GenerateSongView ..> GenerationJob : creates
    GenerateSongView ..> SongGeneratorStrategy : delegates to
    GenerationStatusView ..> GenerationJob : polls
    GenerationStatusView ..> SongGeneratorStrategy : polls via

    %% ════════════════════════════════════════════
    %% TEMPLATE LAYER (MVT)
    %% ════════════════════════════════════════════

    class Templates {
        <<Template>>
        base.html
        library.html
        studio.html
        player.html
        login.html
        register.html
    }

    %% External Service Connections
    Creator ..> GoogleOAuth : authenticates via
```

## Architecture Summary (MVT)

| Layer | Components | Files |
|---|---|---|
| **Model** | `User`, `Creator`, `Listener`, `Library`, `Song`, `GenerationJob`, `Genre`, `Mood`, `Occasion` | `domain/models/*.py` |
| **View** | `CreatorViewSet`, `ListenerViewSet`, `LibraryViewSet`, `SongViewSet`, `GenerateSongView`, `GenerationStatusView` + frontend views | `domain/views/*.py` |
| **Template** | `base.html`, `library.html`, `studio.html`, `player.html`, `login.html`, `register.html` | `domain/templates/domain/*.html` |
| **Strategy** | `SongGeneratorStrategy` (ABC), `MockSongGeneratorStrategy`, `SunoSongGeneratorStrategy` | `domain/generation/*.py` |
| **Serializer** | `CreatorSerializer`, `ListenerSerializer`, `LibrarySerializer`, `SongSerializer`, `GenerationRequestSerializer`, `GenerationJobSerializer` | `domain/serializers/*.py` |

## What Changed from v1.0

### Song class — new attributes:
- `audio_url`: URL — stores the link to the generated audio file
- `is_deleted`: Boolean — implements the soft-deletion pattern described in the original domain model assumptions

### GenerationJob — entirely new class:
- Tracks async song-generation tasks
- Links to Song via ForeignKey
- Records which strategy was used (Mock vs Suno)
- Stores intermediate status updates (PENDING → TEXT_SUCCESS → FIRST_SUCCESS → SUCCESS)

### Strategy Pattern — new class hierarchy:
- `SongGeneratorStrategy` (abstract base class)
- `MockSongGeneratorStrategy` (offline, deterministic generation for development)
- `SunoSongGeneratorStrategy` (real AI generation via Suno API)
- Selected at runtime via `get_generator()` factory function and `GENERATOR_STRATEGY` setting
