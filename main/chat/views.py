from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Chat, Message
from .forms import MessageForm, CodeAnalysisForm
from .services import OllamaService

ollama_service = OllamaService()

#All chats
@login_required
def chat_list(request):
    chats = Chat.objects.filter(user=request.user)

    # Если нет чатов, создаем первый
    if not chats.exists():
        first_chat = Chat.objects.create(
            user=request.user,
            title='Первый чат'
        )
        return redirect('ai:chat_detail', chat_id=first_chat.id)

    # Перенаправляем на последний активный чат
    last_chat = chats.first()
    return redirect('ai:chat_detail', chat_id=last_chat.id)

#main page
@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    chats = Chat.objects.filter(user=request.user)
    messages_list = chat.messages.all()

    message_form = MessageForm()
    code_form = CodeAnalysisForm()

    context = {
        'chat': chat,
        'chats': chats,
        'messages': messages_list,
        'message_form': message_form,
        'code_form': code_form,
    }

    return render(request, 'chat/ai_chat.html', context)

#new chat
@login_required
def create_chat(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Новый чат')
        chat = Chat.objects.create(
            user=request.user,
            title=title
        )
        messages.success(request, 'Чат создан!')
        return redirect('ai:chat_detail', chat_id=chat.id)

    # Если GET - создаем чат с дефолтным названием
    chat = Chat.objects.create(
        user=request.user,
        title='Новый чат'
    )
    return redirect('ai:chat_detail', chat_id=chat.id)

#massange send
@login_required
def send_message(request, chat_id):
    """Отправка сообщения с ответом от Ollama"""
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']

            # Сохраняем сообщение пользователя
            user_message = Message.objects.create(
                chat=chat,
                role='user',
                content=content
            )

            # Получаем историю чата для контекста
            chat_history = chat.messages.filter(id__lt=user_message.id).order_by('created_at')

            # Получаем ответ от Ollama
            try:
                ai_response = ollama_service.general_chat(
                    message=content,
                    chat_history=chat_history
                )
            except Exception as e:
                ai_response = f"Ошибка при обращении к нейросети: {str(e)}\n\nПроверьте, запущен ли Docker с Ollama."
                messages.error(request, 'Ошибка подключения к Ollama')

            # Сохраняем ответ
            ai_message = Message.objects.create(
                chat=chat,
                role='assistant',
                content=ai_response
            )

            # Генерируем название чата если это первое сообщение
            if chat.messages.count() <= 2:
                try:
                    new_title = ollama_service.generate_title(content)
                    chat.title = new_title
                except:
                    chat.title = content[:30] + ('...' if len(content) > 30 else '')
                chat.save()

            chat.save()
            messages.success(request, 'Сообщение отправлено')

    return redirect('ai:chat_detail', chat_id=chat.id)

@login_required
def analyze_code(request, chat_id):
    """Анализ кода через Ollama"""
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)

    if request.method == 'POST':
        form = CodeAnalysisForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            language = form.cleaned_data['language']

            # Сохраняем сообщение пользователя
            user_message = Message.objects.create(
                chat=chat,
                role='user',
                content=f"🔍 Анализ кода на {language}:\n\n```{language}\n{code}\n```"
            )

            # Получаем ответ от Ollama
            try:
                ai_response = ollama_service.analyze_code(code, language)
                messages.success(request, 'Код проанализирован!')
            except Exception as e:
                ai_response = f"❌ Ошибка при анализе кода: {str(e)}"
                messages.error(request, 'Ошибка при анализе кода')

            # Сохраняем ответ
            ai_message = Message.objects.create(
                chat=chat,
                role='assistant',
                content=ai_response
            )

            # Обновляем название если нужно
            if chat.messages.count() <= 2:
                chat.title = f"Анализ {language} кода"
                chat.save()

            chat.save()

    return redirect('ai:chat_detail', chat_id=chat.id)


@login_required
def delete_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    chat.delete()
    messages.success(request, 'Чат удален!')
    return redirect('ai:chat_list')


@login_required
def regenerate_message(request, message_id):
    """Перегенерировать ответ ассистента"""
    message = get_object_or_404(Message, id=message_id, chat__user=request.user)

    if message.role != 'assistant':
        messages.error(request, 'Можно перегенерировать только ответы ассистента')
        return redirect('chat_detail', chat_id=message.chat.id)

    # Находим сообщение пользователя перед этим ответом
    user_message = Message.objects.filter(
        chat=message.chat,
        role='user',
        created_at__lt=message.created_at
    ).order_by('-created_at').first()

    if user_message:
        try:
            # Генерируем новый ответ
            new_response = ollama_service.general_chat(
                message=user_message.content,
                chat_history=message.chat.messages.filter(created_at__lt=user_message.created_at)
            )

            # Обновляем сообщение
            message.content = new_response
            message.save()
            messages.success(request, 'Ответ перегенерирован')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')

    return redirect('chat_detail', chat_id=message.chat.id)