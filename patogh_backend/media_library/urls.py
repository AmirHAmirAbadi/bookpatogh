from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    PdfItemViewSet, PodcastViewSet, PodcastEpisodeViewSet,
    download_pdf, download_podcast_episode,
)

router = DefaultRouter()
router.register('pdfs', PdfItemViewSet, basename='pdfitem')
router.register('podcasts', PodcastViewSet, basename='podcast')
router.register('podcast-episodes', PodcastEpisodeViewSet, basename='podcastepisode')

urlpatterns = router.urls + [
    path('pdfs/<str:id>/download/', download_pdf, name='pdf-download'),
    path('podcast-episodes/<str:id>/download/', download_podcast_episode, name='podcast-episode-download'),
]
