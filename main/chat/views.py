import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Chat, Message
from .serializers import ChatSerializer


@login_required
def chat_app(request, chat_id=None):
    user_chats = Chat.objects.filter(user=request.user).order_by('-updated_at')

    current_chat = None
    messages = []
    if chat_id:
        current_chat = get_object_or_404(Chat, id=chat_id, user=request.user)
        messages = current_chat.messages.all().order_by('created_at')

    context = {
        'user_chats': user_chats,
        'current_chat': current_chat,
        'messages': messages,
    }
    return render(request, "chat/ai_chat.html")


@login_required
@require_POST
def create_chat_api(request):
    """Создание нового пустого чата"""
    try:
        new_chat = Chat.objects.create(
            user=request.user,
            title="Новый чат"
        )
        return JsonResponse({
            'success': True,
            'chat': {
                'id': new_chat.id,
                'title': new_chat.title,
                'updated_at': new_chat.updated_at.strftime("%Y-%m-%d %H:%M")
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def send_message_api(request):
    """Отправка сообщения и получение ответа от нейросети"""
    data = json.loads(request.body)
    chat_id = data.get('chat_id')
    prompt = data.get('message', '').strip()

    if not prompt:
        return JsonResponse({'success': False, 'error': 'Пустое сообщение'}, status=400)

    # Логика создания чата "на лету"
    if chat_id:
        chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    else:
        # Создаем новый чат с названием из первого сообщения
        title = prompt[:30] + ('...' if len(prompt) > 30 else '')
        chat = Chat.objects.create(user=request.user, title=title)

    # Сохраняем сообщение пользователя
    user_message = Message.objects.create(
        chat=chat,
        role='user',
        content=prompt
    )

    # Обновляем дату изменения чата
    chat.save()  # auto_now=True сработает

    # --- ЭМУЛЯЦИЯ ОТВЕТА НЕЙРОСЕТИ ---
    # Замените этот блок на реальный вызов LLM (ChatGPT, Claude, local LLM)
    # В реальном проекте здесь может быть вызов Celery задачи или синхронный запрос к API
    import time
    time.sleep(0.5)  # Имитация задержки сети (для демонстрации индикатора набора текста)
    ai_response_text = f"Это тестовый ответ от нейросети на запрос: '{prompt}'. Вы находитесь в чате #{chat.id}"
    # ---------------------------------

    ai_message = Message.objects.create(
        chat=chat,
        role='assistant',
        content=ai_response_text
    )

    return JsonResponse({
        'success': True,
        'chat_id': chat.id,
        'user_message': {
            'id': user_message.id,
            'content': user_message.content,
            'created_at': user_message.created_at.strftime("%H:%M")
        },
        'ai_message': {
            'id': ai_message.id,
            'content': ai_message.content,
            'created_at': ai_message.created_at.strftime("%H:%M")
        },
        'chat_title': chat.title
    })