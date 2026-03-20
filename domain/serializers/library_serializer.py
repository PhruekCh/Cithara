from rest_framework import serializers

from domain.models import Library


class LibrarySerializer(serializers.ModelSerializer):
    total_songs_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Library
        fields = [
            'id',
            'creator',
            'date_created',
            'total_songs_count',
        ]
        read_only_fields = ['id', 'date_created', 'total_songs_count']
