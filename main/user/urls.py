from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from . import views

app_name = 'user'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('registr/', views.registr, name='registr'),
    path('profile/', views.profile, name='profile'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)