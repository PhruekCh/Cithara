from django.urls import path, include
from rest_framework.routers import DefaultRouter

from domain.views import (
    CreatorViewSet,
    ListenerViewSet,
    LibraryViewSet,
    SongViewSet,
)

router = DefaultRouter()
router.register(r'creators', CreatorViewSet)
router.register(r'listeners', ListenerViewSet)
router.register(r'libraries', LibraryViewSet)
router.register(r'songs', SongViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
