"""
Mock song-generation strategy.

Produces deterministic, predictable output without any network calls.
Ideal for development, testing, and offline usage.
"""

import uuid

from .base import SongGeneratorStrategy


# ---------------------------------------------------------------------------
# In-memory store so check_status can return whatever generate() created.
# Perfectly fine for dev / single-process testing.
# ---------------------------------------------------------------------------
_mock_jobs: dict[str, dict] = {}


class MockSongGeneratorStrategy(SongGeneratorStrategy):
    """Offline, deterministic song generator — no external API required."""

    def generate(self, request: dict) -> dict:
        task_id = str(uuid.uuid4())

        result = {
            "task_id": task_id,
            "status": "SUCCESS",
            "data": {
                "sunoData": [
                    {
                        "id": str(uuid.uuid4()),
                        "audioUrl": "https://example.com/mock-audio.mp3",
                        "streamAudioUrl": "https://example.com/mock-stream",
                        "imageUrl": "https://example.com/mock-cover.jpeg",
                        "prompt": request.get("prompt", ""),
                        "title": request.get("title", "Mock Song"),
                        "tags": request.get("style", "pop"),
                        "duration": 180.0,
                    }
                ]
            },
        }

        _mock_jobs[task_id] = result
        return result

    def check_status(self, task_id: str) -> dict:
        if task_id in _mock_jobs:
            return _mock_jobs[task_id]

        # Unknown task_id — return a generic SUCCESS stub
        return {
            "task_id": task_id,
            "status": "SUCCESS",
            "data": {
                "sunoData": [
                    {
                        "id": "mock-unknown",
                        "audioUrl": "https://example.com/mock-audio.mp3",
                        "streamAudioUrl": "https://example.com/mock-stream",
                        "imageUrl": "https://example.com/mock-cover.jpeg",
                        "prompt": "",
                        "title": "Mock Song",
                        "tags": "pop",
                        "duration": 180.0,
                    }
                ]
            },
        }
