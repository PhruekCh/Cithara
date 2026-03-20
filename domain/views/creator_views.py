from rest_framework.viewsets import ModelViewSet

from domain.models import Creator
from domain.serializers import CreatorSerializer


class CreatorViewSet(ModelViewSet):
    """
    CRUD operations for Creator.

    list:       GET    /creators/
    create:     POST   /creators/
    retrieve:   GET    /creators/{id}/
    update:     PUT    /creators/{id}/
    partial:    PATCH  /creators/{id}/
    destroy:    DELETE /creators/{id}/
    """
    queryset = Creator.objects.all()
    serializer_class = CreatorSerializer
