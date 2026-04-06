from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.urls import path, include, reverse_lazy

from . import views

app_name = 'user'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('registr/', views.registr, name='registr'),
    path('profile/', views.profile, name='profile'),
    path('password-reset/',
        PasswordResetView.as_view(
            template_name="user/password_reset_form.html",
            email_template_name="user/password_reset_email.html",
            success_url=reverse_lazy("user:password_reset_done")
        ),
        name='password_reset'),
    path('password-reset/done/',
        PasswordResetDoneView.as_view(template_name="user/password_reset_done.html",),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(template_name="user/password_reset_confirm.html",
                                         success_url=reverse_lazy("user:password_reset_complete")),
        name='password_reset_confirm'),
    path('reset/done/',
        PasswordResetCompleteView.as_view(template_name="user/password_reset_complete.html",),
        name='password_reset_complete'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)