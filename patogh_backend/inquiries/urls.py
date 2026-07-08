from rest_framework.routers import DefaultRouter

from .views import BookRequestViewSet

router = DefaultRouter()
router.register('requests', BookRequestViewSet, basename='bookrequest')

urlpatterns = router.urls
