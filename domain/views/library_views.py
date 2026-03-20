from rest_framework.viewsets import ModelViewSet

from domain.models import Library
from domain.serializers import LibrarySerializer


class LibraryViewSet(ModelViewSet):
    """
    CRUD operations for Library.

    list:       GET    /libraries/
    create:     POST   /libraries/
    retrieve:   GET    /libraries/{id}/
    update:     PUT    /libraries/{id}/
    partial:    PATCH  /libraries/{id}/
    destroy:    DELETE /libraries/{id}/
    """
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
