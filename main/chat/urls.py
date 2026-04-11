from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from . import views

app_name = 'ai'

urlpatterns = [
    path('chat/', views.chat, name='chat'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)