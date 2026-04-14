    function clearEditor() {
            document.querySelector('.code-editor').value = '';
        }

        // Автоскролл вниз при загрузке
        window.onload = function() {
            var chatMessages = document.querySelector('.chat-messages');
            chatMessages.scrollTop = chatMessages.scrollHeight;
        };

        // Отправка по Ctrl+Enter
        document.querySelector('.chat-input').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                this.closest('form').submit();
            }
        });