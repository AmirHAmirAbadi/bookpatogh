from django.urls import path

from .views import AIChatView, AISeoView

urlpatterns = [
    path('ai/chat/', AIChatView.as_view(), name='ai-chat'),
    path('ai/seo/', AISeoView.as_view(), name='ai-seo'),
]
