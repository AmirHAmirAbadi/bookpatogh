from django.urls import path

from .views import AIChatView

urlpatterns = [
    path('ai/chat/', AIChatView.as_view(), name='ai-chat'),
]
