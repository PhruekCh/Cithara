from rest_framework.viewsets import ModelViewSet

from domain.models import Song
from domain.serializers import SongSerializer


class SongViewSet(ModelViewSet):
    """
    CRUD operations for Song.

    list:       GET    /songs/
    create:     POST   /songs/
    retrieve:   GET    /songs/{id}/
    update:     PUT    /songs/{id}/
    partial:    PATCH  /songs/{id}/
    destroy:    DELETE /songs/{id}/
    """
    queryset = Song.objects.all()
    serializer_class = SongSerializer
