from rest_framework import permissions, viewsets

from catalog.views import IsAdminOrReadOnly
from .models import Comment, Post
from .serializers import CommentSerializer, PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        if user and user.is_authenticated and user.is_staff:
            return Post.objects.all()
        return Post.objects.filter(published=True)


class IsAdminOrReadCreate(permissions.BasePermission):
    """Anyone can read approved comments and post a new one (guest included);
    only staff can edit/moderate/delete comments."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS or request.method == 'POST':
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAdminOrReadCreate]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        qs = Comment.objects.all()
        post_id = self.request.query_params.get('post')
        if post_id:
            qs = qs.filter(post_id=post_id)
        if not (user and user.is_authenticated and user.is_staff):
            qs = qs.filter(approved=True)
        return qs

    def perform_create(self, serializer):
        # guests can never self-approve or self-reject; new comments are always
        # auto-approved (moderation, if needed, happens afterwards from the admin panel)
        serializer.save(approved=True)
