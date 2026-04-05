from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    image = models.ImageField(
        upload_to='users_images',
        blank=True,
        null=True,
        default=None,  # Явно указываем значение по умолчанию
        verbose_name='Аватар'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='О себе',
    )
    website = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Веб-сайт',
    )
    github = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='GitHub',
    )
    linkedin = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='LinkedIn',
    )

    class Meta:
        db_table= 'user'

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Объединяем оба метода в один
        if not self.username:
            if self.email:
                self.username = self.email.split('@')[0]
            else:
                self.username = f"user_{self.pk if self.pk else 'temp'}"

        # Автоматически добавляем префикс папки если его нет
        if self.image and self.image.name and not self.image.name.startswith('users_images/'):
            self.image.name = f'users_images/{self.image.name}'

        super().save(*args, **kwargs)

    def get_avatar_url(self):
        """Безопасное получение URL аватарки"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None