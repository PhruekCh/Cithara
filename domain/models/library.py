from django.db import models

from .creator import Creator


class Library(models.Model):
    """
    The personal collection of a Creator.
    One Creator has exactly one Library (1-to-1).
    Matches domain class: Library.
    """
    creator      = models.OneToOneField(
        Creator,
        on_delete=models.CASCADE,
        related_name='library'
    )
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Library"
        verbose_name_plural = "Libraries"

    @property
    def total_songs_count(self):
        """Derived attribute — always reflects actual count."""
        return self.songs.count()

    def __str__(self):
        return f"{self.creator.display_name}'s Library"
