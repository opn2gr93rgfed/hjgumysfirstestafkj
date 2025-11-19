"""
Тестовый скрипт для проверки обработки попапов для Octo Browser
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from src.utils.playwright_parser import PlaywrightParser

# Тестовый Playwright код с expect_popup
test_code = '''
from playwright.sync_api import Playwright, sync_playwright

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://example.com")

    # ПОПАП 1: Стандартная конструкция
    with page.expect_popup() as page1_info:
        page.get_by_role("button", name="View my quotes").click()
    page1 = page1_info.value
    page1.goto("https://quotes.example.com")

    # ПОПАП 2: С несколькими действиями внутри with
    with page.expect_popup() as page2_info:
        page.get_by_role("button", name="Open form").click()
        page.wait_for_timeout(500)
    page2 = page2_info.value
    page2.get_by_role("heading", name="Application Form").wait_for(state="visible")

    # Обычное действие (не попап)
    page.get_by_role("button", name="Submit").click()

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
'''

print("=" * 80)
print("ТЕСТ ОБРАБОТКИ ПОПАПОВ ДЛЯ OCTO BROWSER")
print("=" * 80)

parser = PlaywrightParser()
result = parser.parse_playwright_code(test_code)

print("\n[1] ОРИГИНАЛЬНЫЙ КОД:")
print("-" * 80)
print(test_code[:600])

print("\n[2] НАЙДЕНО ДЕЙСТВИЙ:", len(result['actions']))

print("\n[3] КОНВЕРТИРОВАННЫЙ КОД С ОБРАБОТКОЙ ПОПАПОВ:")
print("-" * 80)
converted = result['converted_code']
# Показать первую часть с функциями
lines = converted.split('\n')
for i, line in enumerate(lines[:100]):
    print(f"{i+1:3}: {line}")

print("...\n")

print("\n[4] ПРОВЕРКА ТРАНСФОРМАЦИИ:")
print("-" * 80)

# Проверяем что функция wait_and_switch_to_popup добавлена
if 'def wait_and_switch_to_popup' in converted:
    print("✅ Функция wait_and_switch_to_popup добавлена")
else:
    print("❌ Функция wait_and_switch_to_popup НЕ найдена")

# Проверяем замену попапов
if 'page1 = wait_and_switch_to_popup(' in converted:
    print("✅ Попап 1 заменен на wait_and_switch_to_popup")
else:
    print("❌ Попап 1 НЕ заменен")

if 'page2 = wait_and_switch_to_popup(' in converted:
    print("✅ Попап 2 заменен на wait_and_switch_to_popup")
else:
    print("❌ Попап 2 НЕ заменен")

# Проверяем что старые конструкции удалены
if 'with page.expect_popup()' in converted:
    print("❌ Старые with page.expect_popup() не удалены")
else:
    print("✅ Старые with page.expect_popup() удалены")

if 'page1_info.value' in converted or 'page2_info.value' in converted:
    print("❌ Старые .value конструкции не удалены")
else:
    print("✅ Старые .value конструкции удалены")

# Проверяем что обычные кнопки остались
if 'await smart_click_button("Submit")' in converted:
    print("✅ Обычная кнопка Submit осталась как smart_click_button")
else:
    print("❌ Обычная кнопка изменена")

print("\n" + "=" * 80)
print("ПРОВЕРКА ФИНАЛЬНЫХ ВЫЗОВОВ ПОПАПОВ")
print("=" * 80)

# Вывести строки с wait_and_switch_to_popup
for i, line in enumerate(lines):
    if 'wait_and_switch_to_popup' in line and 'def wait_and_switch_to_popup' not in line:
        # Показать контекст
        print(f"Строка {i+1}:")
        for j in range(max(0, i-1), min(len(lines), i+3)):
            print(f"  {j+1}: {lines[j]}")
        print()

print("=" * 80)
print("ТЕСТ ЗАВЕРШЕН")
print("=" * 80)
