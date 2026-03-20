from rest_framework.viewsets import ModelViewSet

from domain.models import Listener
from domain.serializers import ListenerSerializer


class ListenerViewSet(ModelViewSet):
    """
    CRUD operations for Listener.

    list:       GET    /listeners/
    create:     POST   /listeners/
    retrieve:   GET    /listeners/{id}/
    update:     PUT    /listeners/{id}/
    partial:    PATCH  /listeners/{id}/
    destroy:    DELETE /listeners/{id}/
    """
    queryset = Listener.objects.all()
    serializer_class = ListenerSerializer
