"""
Suno API song-generation strategy.

Integrates with https://api.sunoapi.org to create real AI-generated music.
Requires a valid SUNO_API_KEY in Django settings / environment.
"""

import requests
from django.conf import settings

from .base import SongGeneratorStrategy

SUNO_BASE_URL = "https://api.sunoapi.org/api/v1"


class SunoSongGeneratorStrategy(SongGeneratorStrategy):
    """Real song generator that calls the Suno API."""

    def __init__(self):
        self.api_key = getattr(settings, 'SUNO_API_KEY', '')
        if not self.api_key:
            raise ValueError(
                "SUNO_API_KEY is not set. "
                "Add it to your .env file or Django settings."
            )

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # Strategy interface
    # ------------------------------------------------------------------
    def generate(self, request: dict) -> dict:
        """
        POST https://api.sunoapi.org/api/v1/generate

        Sends a generation request and returns the taskId.
        """
        payload = {
            "customMode": False,
            "instrumental": False,
            "model": "V4",
            "prompt": request.get("prompt", ""),
            "style": request.get("style", "Pop"),
            "title": request.get("title", "Untitled"),
            "callBackUrl": "https://httpbin.org/post",  # publicly reachable; replace with your real endpoint in production
        }

        response = requests.post(
            f"{SUNO_BASE_URL}/generate",
            headers=self._headers(),
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        body = response.json()

        # body.data may be a dict {"taskId": "..."} or a list [{"taskId": "..."}]
        data = body.get("data") or {}
        if isinstance(data, list):
            data = data[0] if data else {}
        task_id = data.get("taskId", "")

        return {
            "task_id": task_id,
            "status": "PENDING",
            "data": None,
        }

    def check_status(self, task_id: str) -> dict:
        """
        GET https://api.sunoapi.org/api/v1/generate/record-info?taskId=<id>

        Polls the Suno API for task status and results.
        """
        response = requests.get(
            f"{SUNO_BASE_URL}/generate/record-info",
            headers=self._headers(),
            params={"taskId": task_id},
            timeout=30,
        )
        response.raise_for_status()
        body = response.json()

        data = body.get("data", {})

        return {
            "task_id": data.get("taskId", task_id),
            "status": data.get("status", "PENDING"),
            "data": data.get("response"),
            "error_message": data.get("errorMessage"),
        }
