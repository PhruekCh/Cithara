from rest_framework import serializers

from domain.models import Song


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = [
            'id',
            'library',
            'title',
            'duration',
            'genre',
            'mood',
            'occasion',
            'audio_url',
            'date_generated',
            'is_deleted',
        ]
        read_only_fields = ['id', 'date_generated']
