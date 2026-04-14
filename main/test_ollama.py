# test_ollama.py
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from chat.services import OllamaService


def test_ollama():
    print("🔍 Тестирование подключения к Ollama...")

    service = OllamaService()

    # Проверяем доступные модели
    print("\n📋 Доступные модели:")
    models = service.get_available_models()
    if models:
        for model in models:
            print(f"  - {model}")
    else:
        print("  ❌ Модели не найдены")

    # Тестовый запрос
    print("\n💬 Тестовый запрос...")
    response = service.general_chat("Привет! Как дела?")
    print(f"Ответ: {response[:200]}...")

    print("\n✅ Тест завершен!")


if __name__ == "__main__":
    test_ollama()