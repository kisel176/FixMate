from django.db import models

from django.db import models
from django.utils import timezone

from user.models import User


class Chat(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chats',
        verbose_name='Пользователь'
    )

    title = models.CharField(
        max_length=255,
        default='Новый чат',
        verbose_name='Название чата'
    )

    # Системные поля
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата последнего обновления'
    )

    # Дополнительные полезные поля
    is_archived = models.BooleanField(
        default=False,
        verbose_name='Архивирован',
        help_text='Скрыть из основного списка, но не удалять'
    )

    # Опционально: для подсчета сообщений без запросов к связанной таблице
    message_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество сообщений'
    )

    # Опционально: для поддержки разных моделей нейросетей
    model_name = models.CharField(
        max_length=50,
        default='gpt-3.5-turbo',
        verbose_name='Используемая модель',
        blank=True
    )

    # Опционально: настройки для конкретного чата
    system_prompt = models.TextField(
        blank=True,
        default='',
        verbose_name='Системный промпт',
        help_text='Инструкция для нейросети в этом чате'
    )

    temperature = models.FloatField(
        default=0.7,
        verbose_name='Температура',
        help_text='От 0 до 2. Выше - более креативные ответы'
    )

    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['user', 'is_archived']),
        ]

    def __str__(self):
        return f'{self.title} ({self.user.username})'

    def update_message_count(self):
        """Обновить счетчик сообщений (вызывать при добавлении/удалении)"""
        self.message_count = self.messages.count()
        self.save(update_fields=['message_count'])

    def get_last_message(self):
        """Получить последнее сообщение в чате"""
        return self.messages.order_by('-created_at').first()

    def get_preview(self, length=50):
        """Получить превью последнего сообщения для отображения в списке"""
        last_msg = self.get_last_message()
        if last_msg:
            return last_msg.content[:length] + ('...' if len(last_msg.content) > length else '')
        return 'Нет сообщений'


class Message(models.Model):
    """
    Модель для хранения отдельных сообщений в чате
    """

    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        ASSISTANT = 'assistant', 'Ассистент'
        SYSTEM = 'system', 'Системное'
        ERROR = 'error', 'Ошибка'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        PROCESSING = 'processing', 'Обрабатывается'
        COMPLETED = 'completed', 'Завершено'
        FAILED = 'failed', 'Ошибка'

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Чат'
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль',
        db_index=True
    )

    content = models.TextField(
        verbose_name='Текст сообщения'
    )

    # Системные поля
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время отправки',
        db_index=True
    )

    # Опционально: для отслеживания статуса обработки
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.COMPLETED,
        verbose_name='Статус'
    )

    # Опционально: для аналитики и отладки
    tokens_used = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Использовано токенов'
    )

    processing_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Время обработки (сек)'
    )

    # Опционально: для работы с разными провайдерами
    provider = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='Провайдер',
        help_text='openai, anthropic, local, etc.'
    )

    # Опционально: хранение метаданных
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Метаданные',
        help_text='Дополнительная информация (finish_reason, model и т.д.)'
    )

    # Опционально: для поддержки редактирования сообщений
    is_edited = models.BooleanField(
        default=False,
        verbose_name='Отредактировано'
    )

    edited_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Время редактирования'
    )

    # Опционально: связь с конкретной версией ответа (если делаете регенерацию)
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='versions',
        verbose_name='Родительское сообщение',
        help_text='Для отслеживания версий ответов'
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chat', 'created_at']),
            models.Index(fields=['chat', 'role']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'{self.role}: {self.content[:50]}...'

    def save(self, *args, **kwargs):
        """Переопределяем save для автоматического обновления счетчика в чате"""
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            # Обновляем счетчик сообщений в чате
            self.chat.message_count = models.F('message_count') + 1
            self.chat.save(update_fields=['message_count', 'updated_at'])

    def get_formatted_time(self):
        """Возвращает отформатированное время для фронтенда"""
        return self.created_at.strftime('%H:%M')