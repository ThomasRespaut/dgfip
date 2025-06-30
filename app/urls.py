from django.urls import path
from .views import index, chat_view

urlpatterns = [
    path('', index, name='app-index'),
    path("api/chat/", chat_view, name="chat_view"),
]
