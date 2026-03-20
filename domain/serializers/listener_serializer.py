from rest_framework import serializers

from domain.models import Listener


class ListenerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listener
        fields = [
            'id',
            'email',
            'display_name',
            'recently_played',
            'date_joined',
            'last_login',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
