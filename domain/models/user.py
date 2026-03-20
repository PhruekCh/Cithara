from django.db import models


class User(models.Model):
    """
    Abstract base entity. Represents the core identity of any person
    accessing the platform. Matches domain class: User.
    """
    email        = models.EmailField(unique=True)
    display_name = models.CharField(max_length=150)
    date_joined  = models.DateTimeField(auto_now_add=True)
    last_login   = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True  # Not a DB table itself — Creator/Listener are

    def __str__(self):
        return f"{self.display_name} <{self.email}>"
