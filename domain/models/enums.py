from django.db import models


class Genre(models.TextChoices):
    ROCK    = 'rock',    'Rock'
    POP     = 'pop',     'Pop'
    HIPHOP  = 'hiphop',  'Hip-Hop'
    JAZZ    = 'jazz',    'Jazz'
    COUNTRY = 'country', 'Country'


class Mood(models.TextChoices):
    HAPPY     = 'happy',     'Happy'
    SAD       = 'sad',       'Sad'
    ENERGETIC = 'energetic', 'Energetic'
    CALM      = 'calm',      'Calm'


class Occasion(models.TextChoices):
    WORKOUT     = 'workout',     'Workout'
    FUNERAL     = 'funeral',     'Funeral'
    CELEBRATION = 'celebration', 'Celebration'
    RELAXATION  = 'relaxation',  'Relaxation'
