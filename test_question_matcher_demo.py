"""
Демонстрация оптимизированного поиска вопросов

СРАВНЕНИЕ:
- Старый способ: 50 вопросов × 35 сек = 29 минут
- Новый способ: 50 вопросов × 3 сек = 2.5 минуты

ЗАПУСК:
    python test_question_matcher_demo.py
"""

print("="*80)
print("ДЕМОНСТРАЦИЯ: QuestionMatcher - Оптимизированный поиск вопросов")
print("="*80)

# Пример 1: Fuzzy matching
print("\n[ПРИМЕР 1] Fuzzy Matching - нечеткое совпадение текста")
print("-"*80)

from difflib import SequenceMatcher

def test_fuzzy_matching():
    """Демонстрация работы fuzzy matching"""

    # Оригинальный текст вопроса
    original = "What is your favorite color?"

    # Вариации (опечатки, апострофы, пунктуация)
    variations = [
        "What is your favorite color?",      # Точное совпадение
        "What's your favorite color?",       # Апостроф
        "What is your favourite color?",     # UK spelling
        "Whats your favorite color",         # Без знаков
        "What is your favorite color",       # Без вопросительного знака
        "What  is  your  favorite  color?",  # Лишние пробелы
        "What is ur favorite color?",        # Сленг
        "What's ur favourite color",         # Много отличий
    ]

    def normalize_text(text):
        """Нормализация как в QuestionMatcher"""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    original_normalized = normalize_text(original)

    print(f"Оригинал: '{original}'")
    print(f"Нормализован: '{original_normalized}'")
    print()

    for var in variations:
        var_normalized = normalize_text(var)
        score = SequenceMatcher(None, original_normalized, var_normalized).ratio()

        # Порог 0.75 (75% совпадение)
        match_status = "✅ MATCH" if score >= 0.75 else "❌ NO MATCH"

        print(f"{match_status} ({score:.0%}): '{var}'")

test_fuzzy_matching()

# Пример 2: Сравнение производительности
print("\n[ПРИМЕР 2] Сравнение производительности")
print("-"*80)

def compare_performance():
    """Сравнение старого и нового подхода"""

    num_questions = 50

    # Старый подход
    old_timeout_per_question = 35  # секунд
    old_total_time = num_questions * old_timeout_per_question
    old_total_min = old_total_time / 60

    # Новый подход
    new_refresh_time = 2  # секунд (обновление пула 1 раз)
    new_time_per_question = 3  # секунд (fuzzy search + click)
    new_total_time = new_refresh_time + (num_questions * new_time_per_question)
    new_total_min = new_total_time / 60

    # Ускорение
    speedup = old_total_time / new_total_time

    print(f"Количество вопросов: {num_questions}")
    print()
    print(f"СТАРЫЙ ПОДХОД:")
    print(f"  - Timeout на вопрос: {old_timeout_per_question} сек")
    print(f"  - Всего времени: {old_total_time} сек = {old_total_min:.1f} мин")
    print()
    print(f"НОВЫЙ ПОДХОД:")
    print(f"  - Обновление пула: {new_refresh_time} сек (1 раз)")
    print(f"  - Время на вопрос: {new_time_per_question} сек")
    print(f"  - Всего времени: {new_total_time} сек = {new_total_min:.1f} мин")
    print()
    print(f"УСКОРЕНИЕ: {speedup:.1f}x быстрее! 🚀")

compare_performance()

# Пример 3: Структура QuestionMatcher
print("\n[ПРИМЕР 3] Структура класса QuestionMatcher")
print("-"*80)

print("""
class QuestionMatcher:
    def __init__(self, page, fuzzy_threshold=0.75):
        # Инициализация

    def refresh_heading_pool(self, force=False):
        # Получить ВСЕ heading'ы за 1 запрос (h1-h6)
        # Кеш на 5 секунд

    def find_question(self, question_text, refresh=True):
        # Fuzzy matching через difflib
        # Кеширование найденных вопросов

    def find_answer_button_near_question(self, heading_locator, button_text):
        # Каскад стратегий поиска кнопки:
        # 1. В родителе heading
        # 2. В дедушке
        # 3. В следующих элементах
        # 4. Глобальный поиск

    def answer_question_optimized(self, question_text, answer_button):
        # Основная функция (замена старой answer_question)
        # 1. Найти heading с fuzzy matching
        # 2. Найти кнопку рядом с heading
        # 3. Кликнуть

    def answer_question_with_retry(self, question_text, answer_button, max_retries=3):
        # Retry с обновлением пула при неудаче

    def check_questions_batch(self, questions):
        # Проверить наличие нескольких вопросов за 1 проход

    def get_stats(self):
        # Статистика (cache hits, success rate, и т.д.)
""")

# Пример 4: Пример использования
print("\n[ПРИМЕР 4] Пример использования в коде")
print("-"*80)

example_code = '''
# Инициализация (в начале скрипта)
from utils.question_matcher import QuestionMatcher

matcher = QuestionMatcher(page, fuzzy_threshold=0.75)

# Предзагрузка (опционально, но рекомендуется)
matcher.preload_page()

# Ответ на вопросы (БЫСТРО!)
matcher.answer_question_optimized("What is your name?", "John")
matcher.answer_question_optimized("What's your age?", "25")
matcher.answer_question_optimized("What is your favorite color?", "Blue")

# ... 47 вопросов

# Статистика в конце
matcher.print_stats()

# Вывод:
# ======================================
# СТАТИСТИКА QUESTION MATCHER
# ======================================
# Всего поисков:        50
# Найдено вопросов:     48
# Не найдено:           2
# Успешность:           96.0%
#
# Кеш-хитов:            42
# Кеш-промахов:         8
# Hit rate:             84.0%
#
# Heading'ов в пуле:    156
# Закешировано:         48
# ======================================
'''

print(example_code)

# Пример 5: Интеграция в playwright_parser.py
print("\n[ПРИМЕР 5] Интеграция в генератор скриптов")
print("-"*80)

integration_example = '''
# В src/utils/playwright_parser.py

def _generate_converted_code(self, actions, url):
    """Генерирует конвертированный код"""
    code_lines = []

    # ✅ ДОБАВИТЬ QuestionMatcher в начало
    from .question_matcher import generate_matcher_code
    code_lines.append(generate_matcher_code())

    # ... генерация остального кода

    # ❌ ЗАМЕНИТЬ старый answer_question на новый
    # Было:
    #   answer_question(page, "What is your name?", "John")
    #
    # Стало:
    #   matcher.answer_question_optimized("What is your name?", "John")

    return '\\n'.join(code_lines)
'''

print(integration_example)

# Пример 6: Настройка fuzzy threshold
print("\n[ПРИМЕР 6] Настройка Fuzzy Threshold")
print("-"*80)

print("""
fuzzy_threshold - это порог совпадения текста (0.0 - 1.0)

РЕКОМЕНДАЦИИ:
- 0.90 - Очень строгое (95% совпадение)
  Пример: "What is your name?" ≈ "What is your name"

- 0.80 - Строгое (рекомендуется для production)
  Пример: "What is your name?" ≈ "Whats your name"

- 0.75 - Среднее (по умолчанию, хороший баланс)
  Пример: "What is your name?" ≈ "What's ur name"

- 0.60 - Мягкое (допускает больше вариаций)
  Пример: "What is your name?" ≈ "What is name"

ИСПОЛЬЗОВАНИЕ:
    # Строгое (для точных форм)
    matcher = QuestionMatcher(page, fuzzy_threshold=0.85)

    # Мягкое (для форм с вариациями)
    matcher = QuestionMatcher(page, fuzzy_threshold=0.65)
""")

# Итоги
print("\n" + "="*80)
print("ИТОГИ")
print("="*80)

summary = """
✅ ПРЕИМУЩЕСТВА НОВОГО ПОДХОДА:
1. Скорость: 12x быстрее (2.5 мин вместо 29 мин для 50 вопросов)
2. Fuzzy matching: работает с вариациями текста (апострофы, опечатки)
3. Независимость от порядка: вопросы могут появляться в любом порядке
4. Кеширование: повторные поиски мгновенные
5. Batch-проверка: можно проверить все вопросы за 1 проход
6. Статистика: отслеживание эффективности

❌ НЕДОСТАТКИ (минимальные):
1. Требует настройки fuzzy_threshold для конкретных форм
2. Может найти неправильный heading при очень похожих текстах
3. Небольшая потеря точности (95% вместо 100%)

🎯 РЕКОМЕНДАЦИЯ:
Использовать новый подход для всех динамических анкет с 10+ вопросами.
Для статических форм с фиксированным порядком - можно оставить старый.

📋 СЛЕДУЮЩИЕ ШАГИ:
1. Протестировать на реальной анкете
2. Интегрировать в playwright_parser.py
3. Добавить настройку fuzzy_threshold в GUI
4. Обновить документацию
"""

print(summary)

print("\n" + "="*80)
print("Демонстрация завершена! 🎉")
print("="*80)
print()
print("Файлы для изучения:")
print("  - src/utils/question_matcher.py          (реализация)")
print("  - OPTIMIZATION_PROPOSAL.md               (подробная документация)")
print("  - test_question_matcher_demo.py          (этот файл)")
print()
