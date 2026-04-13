from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Chat, Message
from .forms import MessageForm, CodeAnalysisForm


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
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']

            # Сохраняем сообщение пользователя
            Message.objects.create(
                chat=chat,
                role='user',
                content=content
            )

            # Получаем ответ от AI
            ai_response = get_ai_response(content, chat)

            # Сохраняем ответ
            Message.objects.create(
                chat=chat,
                role='assistant',
                content=ai_response
            )

            # Обновляем название чата если это первое сообщение
            if chat.messages.count() <= 2:
                chat.title = content[:30] + ('...' if len(content) > 30 else '')
                chat.save()

            chat.save()  # обновляем updated_at

    return redirect('ai:chat_detail', chat_id=chat.id)

@login_required
def analyze_code(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)

    if request.method == 'POST':
        form = CodeAnalysisForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            language = form.cleaned_data['language']

            # Формируем промпт для AI
            prompt = f"Проанализируй этот код на {language}:\n\n```{language}\n{code}\n```"

            # Сохраняем сообщение пользователя
            Message.objects.create(
                chat=chat,
                role='user',
                content=f"Анализ кода на {language}:\n\n```{language}\n{code}\n```"
            )

            # Получаем ответ от AI
            ai_response = get_ai_response(prompt, chat)

            # Сохраняем ответ
            Message.objects.create(
                chat=chat,
                role='assistant',
                content=ai_response
            )

            chat.save()
            messages.success(request, 'Код проанализирован!')

    return redirect('ai:chat_detail', chat_id=chat.id)


@login_required
def delete_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    chat.delete()
    messages.success(request, 'Чат удален!')
    return redirect('ai:chat_list')


def get_ai_response(prompt, chat):
    pass