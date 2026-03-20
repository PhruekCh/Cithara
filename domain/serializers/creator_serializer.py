from rest_framework import serializers

from domain.models import Creator


class CreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creator
        fields = [
            'id',
            'email',
            'display_name',
            'generation_quota',
            'date_joined',
            'last_login',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
