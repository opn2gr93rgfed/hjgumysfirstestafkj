"""
Тестовый скрипт для проверки умной трансформации пар вопрос-ответ
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from src.utils.playwright_parser import PlaywrightParser

# Тестовый Playwright код с парами heading → button
test_code = '''
from playwright.sync_api import Playwright, sync_playwright

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://example.com/quiz")

    # ПАРА 1: Вопрос → Ответ (должны быть заменены)
    page.get_by_role("heading", name="What is your favorite color?").click()
    page.get_by_role("button", name="Blue").click()

    # ПАРА 2: Вопрос → Ответ с exact=True
    page.get_by_role("heading", name="Do you like Python?").click()
    page.get_by_role("button", name="Yes", exact=True).click()

    # ПАРА 3: Вопрос → промежуточный клик → Ответ (тоже должны заменить)
    page.get_by_role("heading", name="Choose your vehicle").click()
    page.get_by_role("button", name="Car").click()

    # НЕ ПАРА: Вопрос → fill → button (НЕ заменять, это ввод данных)
    page.get_by_role("heading", name="Enter your name").click()
    page.get_by_role("textbox", name="Name").fill("John")
    page.get_by_role("button", name="Submit").click()

    # Обычная кнопка без вопроса (не трогать)
    page.get_by_role("button", name="Next Page").click()

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
'''

print("=" * 80)
print("ТЕСТ УМНОЙ ТРАНСФОРМАЦИИ ПАР ВОПРОС-ОТВЕТ")
print("=" * 80)

parser = PlaywrightParser()
result = parser.parse_playwright_code(test_code)

print("\n[1] ОРИГИНАЛЬНЫЙ КОД:")
print("-" * 80)
print(test_code[:500])

print("\n[2] НАЙДЕНО ДЕЙСТВИЙ:", len(result['actions']))

print("\n[3] КОНВЕРТИРОВАННЫЙ КОД С УМНЫМИ ПАРАМИ:")
print("-" * 80)
print(result['converted_code'])

print("\n[4] ПРОВЕРКА ТРАНСФОРМАЦИИ:")
print("-" * 80)
converted = result['converted_code']

# Проверяем что функция answer_question добавлена
if 'async def answer_question' in converted:
    print("✅ Функция answer_question добавлена")
else:
    print("❌ Функция answer_question НЕ найдена")

# Проверяем замену пар
pairs = [
    ('await answer_question("What is your favorite color?", "Blue")', 'Пара 1: color → Blue'),
    ('await answer_question("Do you like Python?", "Yes", exact=True)', 'Пара 2: Python → Yes (exact)'),
    ('await answer_question("Choose your vehicle", "Car")', 'Пара 3: vehicle → Car'),
]

for expected, description in pairs:
    if expected in converted:
        print(f"✅ {description} заменена на answer_question")
    else:
        print(f"❌ {description} НЕ заменена")

# Проверяем что НЕ-пары НЕ затронуты
if 'await page.get_by_role("heading", name="Enter your name")' in converted:
    print("✅ НЕ-пара (с fill между) НЕ затронута (корректно)")
else:
    print("❌ НЕ-пара была изменена (ошибка)")

# Проверяем что обычная кнопка осталась
if 'await smart_click_button("Next Page")' in converted:
    print("✅ Обычная кнопка без вопроса осталась как smart_click_button")
else:
    print("❌ Обычная кнопка была изменена")

# Проверяем что старые heading clicks удалены
if 'await page.get_by_role("heading", name="What is your favorite color?").click()' in converted:
    print("❌ Старый клик по heading не удален")
else:
    print("✅ Старые клики по heading удалены")

print("\n" + "=" * 80)
print("ТЕСТ ЗАВЕРШЕН")
print("=" * 80)
