document.addEventListener('DOMContentLoaded', function() {

    // ========== СОСТОЯНИЕ ==========
    let currentChatId = null;
    let currentLanguage = 'python';

    // ========== DOM ЭЛЕМЕНТЫ ==========
    const chatList = document.getElementById('chatList');
    const chatMessages = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const newChatBtn = document.getElementById('newChatBtn');
    const codeEditor = document.getElementById('codeEditor');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const chatHeader = document.getElementById('chatHeader');
    const clearCodeBtn = document.getElementById('clearCodeBtn');
    const filename = document.getElementById('filename');
    const langBtns = document.querySelectorAll('.lang-btn');
    const deleteChatBtn = document.getElementById('deleteChatBtn');

    // ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

    function getCSRFToken() {
        return window.CSRF_TOKEN || document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function getCurrentTime() {
        return new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    }

    function formatDate(dateStr) {
        const date = new Date(dateStr);
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);

        if (date.toDateString() === today.toDateString()) {
            return 'Сегодня';
        } else if (date.toDateString() === yesterday.toDateString()) {
            return 'Вчера';
        } else {
            return date.toLocaleDateString('ru-RU');
        }
    }

    function formatMessage(content) {
        // Заменяем код в блоках
        content = content.replace(/```(\w+)?\n([\s\S]*?)```/g, function(match, lang, code) {
            return `<pre><code>${escapeHtml(code.trim())}</code></pre>`;
        });

        // Заменяем инлайн код
        content = content.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Разбиваем на параграфы
        return content.split('\n')
            .map(line => line.trim() ? `<p>${line}</p>` : '')
            .join('');
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // ========== РАБОТА С API ==========

    async function apiCall(url, method = 'GET', body = null) {
        const options = {
            method: method,
            headers: {
                'X-CSRFToken': getCSRFToken(),
            }
        };

        if (body) {
            options.headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(body);
        }

        const response = await fetch(url, options);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.json();
    }

    // ========== ЗАГРУЗКА ДАННЫХ ==========

    async function loadChats() {
        try {
            const chats = await apiCall('/api/chats/');
            renderChatList(chats);

            if (chats.length > 0 && !currentChatId) {
                await loadChat(chats[0].id);
            } else if (chats.length === 0) {
                showWelcomeMessage();
            }
        } catch (error) {
            console.error('Ошибка загрузки чатов:', error);
            showWelcomeMessage();
        }
    }

    function renderChatList(chats) {
        chatList.innerHTML = '';

        chats.forEach(chat => {
            const div = document.createElement('div');
            div.className = `chat-item ${chat.id === currentChatId ? 'active' : ''}`;
            div.dataset.chatId = chat.id;

            div.innerHTML = `
                <div class="chat-name">
                    <span>${escapeHtml(chat.title)}</span>
                    <span class="chat-time">${formatDate(chat.created_at)}</span>
                </div>
                <div class="chat-preview">${escapeHtml(chat.preview || 'Нет сообщений')}</div>
            `;

            div.addEventListener('click', () => loadChat(chat.id));
            chatList.appendChild(div);
        });
    }

    async function loadChat(chatId) {
        try {
            const chat = await apiCall(`/api/chats/${chatId}/`);
            currentChatId = chat.id;

            chatHeader.textContent = chat.title;
            renderMessages(chat.messages);

            document.querySelectorAll('.chat-item').forEach(item => {
                item.classList.toggle('active', item.dataset.chatId == chatId);
            });

        } catch (error) {
            console.error('Ошибка загрузки чата:', error);
        }
    }

    function showWelcomeMessage() {
        chatMessages.innerHTML = `
            <div class="message">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <p>Привет! Я AI ассистент для анализа кода.</p>
                    <p>Загрузите код, и я помогу найти ошибки, оптимизировать и улучшить его.</p>
                    <div class="message-time">${getCurrentTime()}</div>
                </div>
            </div>
        `;
    }

    function renderMessages(messages) {
        chatMessages.innerHTML = '';

        if (!messages || messages.length === 0) {
            showWelcomeMessage();
            return;
        }

        messages.forEach(msg => {
            addMessageToContainer(msg.role, msg.content, msg.created_at);
        });

        scrollToBottom();
    }

    function addMessageToContainer(role, content, time = null) {
        const div = document.createElement('div');
        div.className = `message ${role === 'user' ? 'user' : ''}`;

        const avatar = role === 'user' ? '👤' : '🤖';
        const messageTime = time || getCurrentTime();

        div.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                ${formatMessage(content)}
                <div class="message-time">${messageTime}</div>
            </div>
        `;

        chatMessages.appendChild(div);
        scrollToBottom();
    }

    // ========== ОТПРАВКА СООБЩЕНИЙ ==========

    async function sendMessage() {
        const content = chatInput.value.trim();
        if (!content) return;

        if (!currentChatId) {
            await createNewChat();
        }

        addMessageToContainer('user', content);
        chatInput.value = '';

        showTypingIndicator();

        try {
            const response = await apiCall(
                `/api/chats/${currentChatId}/send/`,
                'POST',
                { content: content }
            );

            hideTypingIndicator();
            addMessageToContainer('assistant', response.ai_message.content);
            await loadChats();

        } catch (error) {
            console.error('Ошибка отправки:', error);
            hideTypingIndicator();
            addMessageToContainer('assistant', 'Извините, произошла ошибка. Попробуйте еще раз.');
        }
    }

    async function createNewChat() {
        try {
            const chat = await apiCall('/api/chats/create/', 'POST', {
                title: 'Новый чат'
            });

            currentChatId = chat.id;
            chatHeader.textContent = chat.title;
            showWelcomeMessage();
            await loadChats();

        } catch (error) {
            console.error('Ошибка создания чата:', error);
        }
    }

    function showTypingIndicator() {
        const div = document.createElement('div');
        div.className = 'message typing';
        div.id = 'typing-indicator';
        div.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <p><em>Печатает...</em></p>
            </div>
        `;
        chatMessages.appendChild(div);
        scrollToBottom();
    }

    function hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) indicator.remove();
    }

    // ========== РАБОТА С КОДОМ ==========

    async function analyzeCode() {
        const code = codeEditor.value.trim();
        if (!code) {
            alert('Введите код для анализа');
            return;
        }

        const prompt = `Проанализируй этот код на ${currentLanguage}:\n\n\`\`\`${currentLanguage}\n${code}\n\`\`\``;
        chatInput.value = prompt;
        await sendMessage();
    }

    function attachCodeToChat() {
        const code = codeEditor.value.trim();
        if (!code) {
            alert('Введите код для прикрепления');
            return;
        }

        chatInput.value = `Вот мой код:\n\n\`\`\`${currentLanguage}\n${code}\n\`\`\``;
        chatInput.focus();
    }

    function clearCode() {
        codeEditor.value = '';
    }

    // ========== ОБРАБОТЧИКИ СОБЫТИЙ ==========

    sendBtn.addEventListener('click', sendMessage);

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    newChatBtn.addEventListener('click', createNewChat);
    analyzeBtn.addEventListener('click', analyzeCode);

    document.getElementById('attachCodeBtn').addEventListener('click', attachCodeToChat);
    clearCodeBtn.addEventListener('click', clearCode);

    // Переключение языка
    langBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            langBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            const lang = this.dataset.lang;
            currentLanguage = lang;

            const filenames = {
                'python': 'main.py',
                'javascript': 'script.js',
                'java': 'Main.java',
                'cpp': 'main.cpp'
            };
            filename.textContent = filenames[lang] || 'code.txt';
        });
    });

    // Удаление чата
    deleteChatBtn.addEventListener('click', async function() {
        if (!currentChatId) return;

        if (!confirm('Удалить этот чат?')) return;

        try {
            await apiCall(`/api/chats/${currentChatId}/delete/`, 'POST');
            currentChatId = null;
            chatHeader.textContent = 'Новый чат';
            await loadChats();
        } catch (error) {
            console.error('Ошибка удаления:', error);
            alert('Не удалось удалить чат');
        }
    });

    // ========== ИНИЦИАЛИЗАЦИЯ ==========
    loadChats();
});