from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from . import views

app_name = 'fixmate'

urlpatterns = [
    path('main/', views.main, name='main'),
    path('ai/', views.ai, name='ai'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)