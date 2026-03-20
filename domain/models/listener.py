from django.db import models

from .user import User


class Listener(User):
    """
    A specialized User who listens to shared content.
    Matches domain class: Listener (inherits User).
    recently_played is modeled as a ManyToMany to Song (ordered).
    """
    recently_played = models.ManyToManyField(
        'Song',
        blank=True,
        related_name='listened_by',
        help_text="Songs this listener has recently played."
    )

    class Meta:
        verbose_name = "Listener"

    def __str__(self):
        return f"[Listener] {self.display_name}"
