// Отправить сообщение
async function sendMessage(chatId, text) {
    const response = await fetch(`/api/chats/${chatId}/send_message/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // надо получить куку
        },
        body: JSON.stringify({content: text})
    });
    return response.json();
}

// Получить CSRF токен (просто скопируй эту функцию)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}