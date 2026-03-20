from django.db import models

from .user import User


class Creator(User):
    """
    A specialized User who can generate music and owns a Library.
    Matches domain class: Creator (inherits User).
    """
    generation_quota = models.PositiveIntegerField(
        default=10,
        help_text="Daily generation limit for this creator."
    )

    class Meta:
        verbose_name = "Creator"

    def __str__(self):
        return f"[Creator] {self.display_name}"
