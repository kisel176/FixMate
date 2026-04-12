from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import ChatViewSet

router = DefaultRouter()
router.register(r'chats', ChatViewSet, basename='chat')
app_name = 'ai'

urlpatterns = [
    path('chat/', views.chat_app, name='chat'),
    path('api/', include(router.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)