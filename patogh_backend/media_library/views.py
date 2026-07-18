from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from catalog.views import IsAdminOrReadOnly
from .models import PdfItem, Podcast, PodcastEpisode
from .serializers import PdfItemSerializer, PodcastSerializer, PodcastEpisodeSerializer


class PdfItemViewSet(viewsets.ModelViewSet):
    serializer_class = PdfItemSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        qs = PdfItem.objects.all()
        if user and user.is_authenticated and user.is_staff:
            return qs
        return qs.filter(published=True)


class PodcastViewSet(viewsets.ModelViewSet):
    serializer_class = PodcastSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        qs = Podcast.objects.prefetch_related('episodes').all()
        if user and user.is_authenticated and user.is_staff:
            return qs
        return qs.filter(published=True)


class PodcastEpisodeViewSet(viewsets.ModelViewSet):
    """Episodes are managed as their own resource (create/edit/delete a single
    part) so the admin panel can add parts to a podcast one at a time without
    re-sending the whole podcast + every other episode."""

    serializer_class = PodcastEpisodeSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'id'

    def get_queryset(self):
        qs = PodcastEpisode.objects.select_related('podcast').all()
        podcast_id = self.request.query_params.get('podcast')
        if podcast_id:
            qs = qs.filter(podcast_id=podcast_id)
        user = self.request.user
        if not (user and user.is_authenticated and user.is_staff):
            qs = qs.filter(podcast__published=True)
        return qs


def _force_download(file_field, download_name):
    if not file_field:
        raise Http404('فایلی برای دانلود موجود نیست.')
    try:
        handle = file_field.open('rb')
    except (FileNotFoundError, ValueError):
        raise Http404('فایل مورد نظر روی سرور پیدا نشد.')
    return FileResponse(handle, as_attachment=True, filename=download_name)


def _is_staff(request):
    return bool(request.user and request.user.is_authenticated and request.user.is_staff)


def download_pdf(request, id):
    """Always-forced download (Content-Disposition: attachment) for a PDF,
    regardless of the storefront's origin — anyone can hit this link since
    every PDF here is free. Staff can also download unpublished drafts to
    preview them before making them live."""
    item = get_object_or_404(PdfItem, id=id) if _is_staff(request) else get_object_or_404(PdfItem, id=id, published=True)
    filename = item.file.name.rsplit('/', 1)[-1] or f'{item.title}.pdf'
    return _force_download(item.file, filename)


def download_podcast_episode(request, id):
    """Forced download for a single podcast episode's audio file."""
    episode = (
        get_object_or_404(PodcastEpisode, id=id) if _is_staff(request)
        else get_object_or_404(PodcastEpisode, id=id, podcast__published=True)
    )
    filename = episode.audio_file.name.rsplit('/', 1)[-1] or f'{episode.title}.mp3'
    return _force_download(episode.audio_file, filename)
