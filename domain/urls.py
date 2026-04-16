from django.urls import path, include
from rest_framework.routers import DefaultRouter

from domain.views import (
    CreatorViewSet,
    ListenerViewSet,
    LibraryViewSet,
    SongViewSet,
    GenerateSongView,
    GenerationStatusView,
)

router = DefaultRouter()
router.register(r'creators', CreatorViewSet)
router.register(r'listeners', ListenerViewSet)
router.register(r'libraries', LibraryViewSet)
router.register(r'songs', SongViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('generate/', GenerateSongView.as_view(), name='generate-song'),
    path(
        'generate/<str:task_id>/status/',
        GenerationStatusView.as_view(),
        name='generation-status',
    ),
]
