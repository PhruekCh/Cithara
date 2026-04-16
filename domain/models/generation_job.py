from django.db import models

from .song import Song


class GenerationJob(models.Model):
    """
    Tracks a song-generation task submitted through any strategy.
    Links to the Song record that was (or will be) produced.
    """

    class Status(models.TextChoices):
        PENDING          = 'PENDING',          'Pending'
        TEXT_SUCCESS      = 'TEXT_SUCCESS',      'Text Success'
        FIRST_SUCCESS     = 'FIRST_SUCCESS',     'First Success'
        SUCCESS           = 'SUCCESS',           'Success'
        FAILED            = 'FAILED',            'Failed'

    class Strategy(models.TextChoices):
        MOCK = 'mock', 'Mock'
        SUNO = 'suno', 'Suno'

    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='generation_jobs',
    )
    task_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique task identifier returned by the generation strategy.",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )
    strategy_used = models.CharField(
        max_length=10,
        choices=Strategy.choices,
    )
    audio_url = models.URLField(blank=True, null=True)
    stream_audio_url = models.URLField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Generation Job"

    def __str__(self):
        return f"Job {self.task_id} [{self.status}]"
