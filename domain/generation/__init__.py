"""
Song-generation strategy module.

Usage:
    from domain.generation import get_generator
    generator = get_generator()
    result = generator.generate({...})
"""

from django.conf import settings


def get_generator():
    """
    Factory that returns the active SongGeneratorStrategy instance
    based on the GENERATOR_STRATEGY Django setting.

    Centralises strategy selection — no if/else scattered elsewhere.
    """
    strategy = getattr(settings, 'GENERATOR_STRATEGY', 'mock')

    if strategy == 'suno':
        from .suno_strategy import SunoSongGeneratorStrategy
        return SunoSongGeneratorStrategy()
    else:
        from .mock_strategy import MockSongGeneratorStrategy
        return MockSongGeneratorStrategy()
