from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'ai'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('create/', views.create_chat, name='create_chat'),
    path('<int:chat_id>/send/', views.send_message, name='send_message'),
    path('<int:chat_id>/analyze/', views.analyze_code, name='analyze_code'),
    path('<int:chat_id>/delete/', views.delete_chat, name='delete_chat'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)