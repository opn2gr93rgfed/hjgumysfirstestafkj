"""
Тестовый скрипт для проверки умной трансформации кнопок
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from src.utils.playwright_parser import PlaywrightParser

# Тестовый Playwright код с разными типами действий
test_code = '''
from playwright.sync_api import Playwright, sync_playwright

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://example.com/form")

    # Должны быть заменены на smart_click_button
    page.get_by_role("button", name="Submit").click()
    page.get_by_role("button", name="Next Step").click()
    page.get_by_role("button", name="Accept", exact=True).click()
    page.get_by_role("button", name="I don't know").click()

    # НЕ должны быть заменены (не кнопки)
    page.get_by_role("textbox", name="Email").fill("test@example.com")
    page.get_by_role("textbox", name="Name").click()
    page.get_by_role("combobox", name="Country").click()
    page.get_by_role("link", name="Privacy Policy").click()

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
'''

print("=" * 80)
print("ТЕСТ УМНОЙ ТРАНСФОРМАЦИИ КНОПОК")
print("=" * 80)

parser = PlaywrightParser()
result = parser.parse_playwright_code(test_code)

print("\n[1] ОРИГИНАЛЬНЫЙ КОД:")
print("-" * 80)
print(test_code)

print("\n[2] НАЙДЕНО ДЕЙСТВИЙ:", len(result['actions']))
for i, action in enumerate(result['actions'], 1):
    print(f"   {i}. {action['type'].upper()}: {action.get('url', action.get('selector', {}).get('chain', 'N/A')[:50])}")

print("\n[3] КОНВЕРТИРОВАННЫЙ КОД С УМНЫМИ КНОПКАМИ:")
print("-" * 80)
print(result['converted_code'])

print("\n[4] ПРОВЕРКА ТРАНСФОРМАЦИИ:")
print("-" * 80)
converted = result['converted_code']

# Проверяем что функция smart_click_button добавлена
if 'def smart_click_button' in converted:
    print("✅ Функция smart_click_button добавлена")
else:
    print("❌ Функция smart_click_button НЕ найдена")

# Проверяем замену button clicks
button_clicks = [
    ('smart_click_button("Submit")', 'Submit button'),
    ('smart_click_button("Next Step")', 'Next Step button'),
    ('smart_click_button("Accept", exact=True)', 'Accept button with exact=True'),
    ('smart_click_button("I don', "I don't know button"),
]

for expected, description in button_clicks:
    if expected in converted:
        print(f"✅ {description} заменен на smart_click_button")
    else:
        print(f"❌ {description} НЕ заменен")

# Проверяем что НЕ-кнопки НЕ затронуты
non_buttons = [
    ('get_by_role("textbox"', 'textbox'),
    ('get_by_role("combobox"', 'combobox'),
    ('get_by_role("link"', 'link'),
]

for pattern, description in non_buttons:
    if pattern in converted:
        print(f"✅ {description} НЕ затронут (корректно)")
    else:
        print(f"❌ {description} был изменен (ошибка)")

print("\n" + "=" * 80)
print("ТЕСТ ЗАВЕРШЕН")
print("=" * 80)
