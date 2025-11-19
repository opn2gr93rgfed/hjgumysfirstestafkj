#!/usr/bin/env python3
"""
ТЕСТ генерируемого скрипта - проверка структуры
"""

import time
from playwright.sync_api import sync_playwright, expect

# ============================================================
# HELPER ФУНКЦИИ (с параметром page)
# ============================================================

def smart_click_button(page, name: str, exact: bool = False):
    """Умный клик по кнопке"""
    locator = page.get_by_role("button", name=name, exact=exact)
    try:
        locator.wait_for(state="visible", timeout=30000)
        if locator.is_visible():
            print(f"[SMART CLICK] Кликаю: {name}")
            locator.click(delay=100)
            page.wait_for_load_state("networkidle", timeout=10000)
    except Exception as e:
        print(f"[SKIP] {name} — {e}")

def answer_question(page, heading: str, answer_button: str, exact: bool = False):
    """Ответ на вопрос"""
    print(f"[ANSWER] Жду вопрос: {heading}")
    heading_locator = page.get_by_role("heading", name=heading, exact=True)
    try:
        heading_locator.wait_for(state="visible", timeout=35000)
        print(f"[ANSWER] Вопрос появился → отвечаю: {answer_button}")
        smart_click_button(page, answer_button, exact=exact)
    except Exception as e:
        print(f"[ANSWER] Пропущено: {e}")

# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def run_automation_iteration(iteration_number: int, data_row: dict):
    """
    Запуск одной итерации

    Args:
        iteration_number: Номер итерации
        data_row: Данные из CSV
    """
    print(f"\n{'='*60}")
    print(f"Итерация #{iteration_number}")
    print(f"Данные: {data_row}")
    print(f"{'='*60}\n")

    try:
        # Подключиться к браузеру через CDP (симуляция)
        cdp_url = "http://127.0.0.1:9222"  # Фейковый URL для теста

        with sync_playwright() as p:
            print(f"[CDP MODE] Подключение к: {cdp_url}")

            # В реальном скрипте здесь будет:
            # browser = p.chromium.connect_over_cdp(cdp_url)
            # context = browser.contexts[0]
            # page = context.pages[0]

            # Для теста просто запускаем обычный браузер
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()  # ← page определён ЗДЕСЬ (12 пробелов)

            print(f"[OK] Страница готова к автоматизации")

            # ============================================================
            # ПОЛЬЗОВАТЕЛЬСКИЙ КОД АВТОМАТИЗАЦИИ (12 пробелов)
            # ============================================================

            # Перейти на сайт
            page.goto("https://example.com", wait_until="domcontentloaded")
            print("[OK] Открыт сайт: https://example.com")

            # Заполнить форму
            # page.fill("#email", data_row.get("email", "test@example.com"))

            # Умный клик (передаём page как параметр!)
            # smart_click_button(page, "Submit")

            # Ответ на вопрос (передаём page!)
            # answer_question(page, "What is your age?", "25-34")

            # ============================================================

            browser.close()
            print(f"[OK] Итерация #{iteration_number} завершена")
            return True

    except Exception as e:
        print(f"[ERROR] Ошибка в итерации #{iteration_number}: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================
# MAIN
# ============================================================

def main():
    """Главная функция"""
    print("="*60)
    print("ТЕСТ ГЕНЕРИРУЕМОГО СКРИПТА")
    print("Проверка: page определён внутри функции")
    print("="*60)

    # Тестовые данные
    data_row = {
        "email": "test@example.com",
        "zip_code": "33071"
    }

    # Запустить одну итерацию
    success = run_automation_iteration(1, data_row)

    if success:
        print("\n✅ ТЕСТ ПРОЙДЕН! Структура правильная!")
        print("✅ page определён внутри run_automation_iteration()")
        print("✅ Helper функции принимают page как параметр")
    else:
        print("\n❌ ТЕСТ ПРОВАЛЕН!")

if __name__ == "__main__":
    main()
