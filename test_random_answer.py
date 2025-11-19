"""
Тестовый скрипт для проверки умной трансформации случайных ответов (#random)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from src.utils.playwright_parser import PlaywrightParser

# Тестовый Playwright код с #random маркерами
test_code = '''
from playwright.sync_api import Playwright, sync_playwright

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://example.com/quiz")

    # ПАРА 1: Вопрос → #random (стандартные параметры)
    page.get_by_role("heading", name="What is your car year?").click()
    #random

    # ПАРА 2: Вопрос → #random[2-5] (кастомные параметры)
    page.get_by_role("heading", name="What is your credit score?").click()
    #random[2-5]

    # ПАРА 3: Вопрос → несколько кнопок → #random (показать варианты)
    page.get_by_role("heading", name="Choose your vehicle type").click()
    page.get_by_role("button", name="Car").click()
    page.get_by_role("button", name="Truck").click()
    page.get_by_role("button", name="SUV").click()
    #random[1-3]

    # НЕ ПАРА: Обычный вопрос с конкретным ответом (не трогать)
    page.get_by_role("heading", name="Do you agree?").click()
    page.get_by_role("button", name="Yes").click()

    # Обычная кнопка без вопроса (не трогать)
    page.get_by_role("button", name="Submit").click()

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
'''

print("=" * 80)
print("ТЕСТ УМНОЙ ТРАНСФОРМАЦИИ СЛУЧАЙНЫХ ОТВЕТОВ (#random)")
print("=" * 80)

parser = PlaywrightParser()
result = parser.parse_playwright_code(test_code)

print("\n[1] ОРИГИНАЛЬНЫЙ КОД:")
print("-" * 80)
print(test_code[:600])

print("\n[2] НАЙДЕНО ДЕЙСТВИЙ:", len(result['actions']))
for i, action in enumerate(result['actions'], 1):
    action_type = action['type'].upper()
    if action_type == 'RANDOM_MARKER':
        print(f"   {i}. {action_type}: min={action['min_options']}, max={action['max_options']}")
    elif action_type == 'GOTO':
        print(f"   {i}. {action_type}: {action['url']}")
    elif action_type == 'CLICK':
        selector_info = action.get('selector', {})
        chain = selector_info.get('chain', 'N/A')[:50]
        print(f"   {i}. {action_type}: {chain}")
    else:
        print(f"   {i}. {action_type}")

print("\n[3] КОНВЕРТИРОВАННЫЙ КОД С УМНЫМИ СЛУЧАЙНЫМИ ОТВЕТАМИ:")
print("-" * 80)
print(result['converted_code'][:2000])
print("...\n")

print("\n[4] ПРОВЕРКА ТРАНСФОРМАЦИИ:")
print("-" * 80)
converted = result['converted_code']

# Проверяем что функция answer_question_random добавлена
if 'async def answer_question_random' in converted:
    print("✅ Функция answer_question_random добавлена")
else:
    print("❌ Функция answer_question_random НЕ найдена")

# Проверяем замену пар
pairs = [
    ('await answer_question_random("What is your car year?")', 'Пара 1: car year → #random'),
    ('await answer_question_random("What is your credit score?", min_options=2, max_options=5)', 'Пара 2: credit score → #random[2-5]'),
    ('await answer_question_random("Choose your vehicle type", min_options=1, max_options=3)', 'Пара 3: vehicle → #random[1-3]'),
]

for expected, description in pairs:
    if expected in converted:
        print(f"✅ {description} заменена на answer_question_random")
    else:
        print(f"❌ {description} НЕ заменена")
        # Отладка
        if 'car year' in description:
            if 'answer_question_random("What is your car year?"' in converted:
                print(f"   → Найдена с другими параметрами")

# Проверяем что НЕ-пары НЕ затронуты
if 'await answer_question("Do you agree?", "Yes")' in converted:
    print("✅ НЕ-пара (конкретный ответ) осталась как answer_question")
else:
    print("❌ НЕ-пара была изменена")

# Проверяем что обычная кнопка осталась
if 'await smart_click_button("Submit")' in converted:
    print("✅ Обычная кнопка без вопроса осталась как smart_click_button")
else:
    print("❌ Обычная кнопка была изменена")

# Проверяем что маркеры удалены
if '# RANDOM_MARKER' in converted:
    print("❌ Маркеры # RANDOM_MARKER не удалены")
else:
    print("✅ Маркеры # RANDOM_MARKER удалены")

print("\n" + "=" * 80)
print("ПРОВЕРКА ФИНАЛЬНОГО КОДА")
print("=" * 80)

# Вывести часть с answer_question_random
lines = converted.split('\n')
for i, line in enumerate(lines):
    if 'answer_question_random' in line and not line.strip().startswith('async def'):
        print(f"Строка {i}: {line}")

print("\n" + "=" * 80)
print("ТЕСТ ЗАВЕРШЕН")
print("=" * 80)
