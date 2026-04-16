from rest_framework import serializers

from domain.models import GenerationJob


class GenerationRequestSerializer(serializers.Serializer):
    """Validates incoming generation requests."""
    prompt   = serializers.CharField(max_length=3000, required=True)
    style    = serializers.CharField(max_length=200, required=True)
    title    = serializers.CharField(max_length=80, required=True)
    genre    = serializers.CharField(max_length=20, required=True)
    mood     = serializers.CharField(max_length=20, required=True)
    occasion = serializers.CharField(max_length=20, required=True)
    library  = serializers.IntegerField(required=True, help_text="Library ID")


class GenerationJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerationJob
        fields = [
            'id',
            'song',
            'task_id',
            'status',
            'strategy_used',
            'audio_url',
            'stream_audio_url',
            'image_url',
            'error_message',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
