"""
Abstract base class defining the song-generation strategy interface.
"""

from abc import ABC, abstractmethod


class SongGeneratorStrategy(ABC):
    """
    Strategy interface for song generation.

    Every concrete strategy must implement:
    - generate(request)  → submit a generation job
    - check_status(task_id) → poll / retrieve results for a task
    """

    @abstractmethod
    def generate(self, request: dict) -> dict:
        """
        Submit a new song-generation task.

        Parameters
        ----------
        request : dict
            Must contain at least:
                prompt  – text description / lyrics
                style   – music style/genre string
                title   – desired song title

        Returns
        -------
        dict
            {"task_id": str, "status": str, ...}
        """

    @abstractmethod
    def check_status(self, task_id: str) -> dict:
        """
        Retrieve the current status and results of a generation task.

        Parameters
        ----------
        task_id : str
            The identifier returned by generate().

        Returns
        -------
        dict
            {"task_id": str, "status": str, "data": {...} | None}
        """
