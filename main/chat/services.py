import ollama
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class OllamaCodeAnalyzer:
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_HOST)
        self.model = settings.OLLAMA_MODEL

    def analyze_code(self, code: str, language: str = None) -> dict:
        """
        Анализирует код и возвращает результат
        """
        try:
            # Формируем промпт для анализа
            prompt = self._create_analysis_prompt(code, language)

            # Отправляем запрос к Ollama
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'Ты - эксперт по анализу кода. Анализируй код, находи ошибки, предлагай улучшения и объясняй сложные моменты.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.3,  # Меньше креативности, больше точности
                    'max_tokens': 2000
                }
            )

            return {
                'success': True,
                'analysis': response['message']['content'],
                'model': self.model
            }

        except Exception as e:
            logger.error(f"Ошибка при обращении к Ollama: {str(e)}")
            return {
                'success': False,
                'error': f'Ошибка соединения с Ollama: {str(e)}'
            }

    def _create_analysis_prompt(self, code: str, language: str = None) -> str:
        """Создает промпт для анализа кода"""
        lang_hint = f" (язык: {language})" if language else ""
        return f"""Проанализируй следующий код{lang_hint} и предоставь подробный анализ:
        Включи в анализ:
        1. Обнаруженные ошибки и потенциальные проблемы
        2. Предложения по улучшению кода
        3. Оптимизацию производительности
        4. Соответствие лучшим практикам
        5. Объяснение сложных участков
        
        Форматируй ответ с использованием markdown для лучшей читаемости."""
