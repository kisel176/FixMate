# chat/services.py
import json
import logging
from django.conf import settings

# Импортируем requests правильно, избегая конфликта с Django
import requests as http_requests

logger = logging.getLogger(__name__)


class OllamaService:
    """Сервис для работы с Ollama API через HTTP"""

    def __init__(self, host=None, model=None):
        self.host = host or getattr(settings, 'OLLAMA_HOST', 'http://localhost:11434')
        # Убираем слеш в конце если есть
        self.host = self.host.rstrip('/')
        self.model = model or getattr(settings, 'OLLAMA_MODEL', 'codellama:7b')
        logger.info(f"OllamaService инициализирован: host={self.host}, model={self.model}")

    def get_available_models(self):
        """Получить список доступных моделей"""
        try:
            response = http_requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                return models
            return []
        except Exception as e:
            logger.error(f"Ошибка получения моделей: {e}")
            return []

    def general_chat(self, message, chat_history=None, model=None):
        """
        Отправка сообщения в чат с учетом истории
        """
        try:
            # Формируем массив сообщений
            messages = [
                {
                    "role": "system",
                    "content": "Ты - AI ассистент для программистов. Помогай с кодом, отвечай на русском языке, будь полезным."
                }
            ]

            # Добавляем историю чата (если есть)
            if chat_history:
                for msg in chat_history:
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })

            # Добавляем текущее сообщение
            messages.append({
                "role": "user",
                "content": message
            })

            # Отправляем запрос
            model_name = model or self.model
            logger.info(f"Отправка запроса к модели: {model_name}")

            response = http_requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": model_name,
                    "messages": messages,
                    "stream": False
                },
                timeout=120  # Увеличиваем таймаут для больших ответов
            )

            if response.status_code == 200:
                result = response.json()
                return result['message']['content']
            else:
                return f"❌ Ошибка API Ollama (код {response.status_code}): {response.text}"

        except http_requests.exceptions.ConnectionError:
            return "❌ Не удалось подключиться к Ollama. Проверьте, запущен ли Docker контейнер на порту 11434"
        except Exception as e:
            logger.error(f"Ошибка в general_chat: {e}")
            return f"❌ Ошибка: {str(e)}"

    def analyze_code(self, code, language, model=None):
        """Анализ кода"""
        prompt = f"""Проанализируй этот код на {language} и дай рекомендации по улучшению:"""""