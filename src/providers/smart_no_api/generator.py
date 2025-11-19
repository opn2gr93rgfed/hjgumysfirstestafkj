# SMART NO API PROVIDER — NO OCTOBROWSER, PURE PLAYWRIGHT WITH FALLBACKS
"""
Provider: smart_no_api
Генератор скриптов БЕЗ Octobrowser API, с умными альтернативами и проверкой заголовков
"""

import json
from typing import Dict, List


class Generator:
    """Генератор для чистого Playwright без API зависимостей"""

    def generate_script(self, user_code: str, config: Dict) -> str:
        """
        Генерирует Playwright скрипт с fallback системой

        Args:
            user_code: Код автоматизации из Playwright recorder
            config: Конфигурация

        Returns:
            Полный исполняемый Python скрипт
        """
        csv_filename = config.get('csv_filename', 'data.csv')
        csv_data = config.get('csv_data', None)
        csv_embed_mode = config.get('csv_embed_mode', True)

        script = self._generate_imports()
        script += self._generate_config(csv_filename, csv_data, csv_embed_mode)
        script += self._generate_helpers()
        script += self._generate_csv_loader()
        script += self._generate_main_iteration(user_code)
        script += self._generate_main_function()

        return script

    def _generate_imports(self) -> str:
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматически сгенерированный скрипт
Provider: smart_no_api (NO OCTOBROWSER API)
"""

import csv
import time
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeout
from typing import Dict, List, Optional

'''

    def _generate_config(self, csv_filename: str, csv_data: List[Dict], csv_embed_mode: bool) -> str:
        config = '''# ============================================================
# КОНФИГУРАЦИЯ
# ============================================================

'''

        if csv_embed_mode and csv_data:
            config += f'''# CSV данные (встроены в скрипт)
CSV_EMBED_MODE = True
CSV_DATA = {json.dumps(csv_data, ensure_ascii=False, indent=2)}

'''
        else:
            config += f'''# CSV файл
CSV_EMBED_MODE = False
CSV_FILENAME = "{csv_filename}"

'''

        config += '''# Настройки браузера
HEADLESS = False
VIEWPORT = {"width": 1920, "height": 1080}
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Таймауты
DEFAULT_TIMEOUT = 30000  # 30 секунд
NAVIGATION_TIMEOUT = 60000  # 60 секунд

'''
        return config

    def _generate_helpers(self) -> str:
        return '''# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def smart_click(page, selectors_list, name="element", timeout=10000):
    """
    Умный клик с альтернативными селекторами

    Args:
        page: Playwright page
        selectors_list: Список альтернативных селекторов
        name: Название элемента для логов
        timeout: Таймаут в миллисекундах
    """
    for i, selector in enumerate(selectors_list, 1):
        try:
            print(f"[SMART_CLICK] Попытка {i}/{len(selectors_list)}: {name}")
            element = page.locator(selector).first
            element.wait_for(state="visible", timeout=timeout)
            element.click()
            print(f"[SMART_CLICK] ✓ Клик выполнен: {name}")
            return True
        except Exception as e:
            print(f"[SMART_CLICK] ✗ Селектор {i} не сработал: {e}")
            if i == len(selectors_list):
                print(f"[SMART_CLICK] ⚠️ Все селекторы не сработали для: {name}")
                return False
    return False


def smart_fill(page, selectors_list, value, name="field", timeout=10000):
    """
    Умное заполнение с альтернативными селекторами

    Args:
        page: Playwright page
        selectors_list: Список альтернативных селекторов
        value: Значение для заполнения
        name: Название поля для логов
        timeout: Таймаут в миллисекундах
    """
    for i, selector in enumerate(selectors_list, 1):
        try:
            print(f"[SMART_FILL] Попытка {i}/{len(selectors_list)}: {name} = {value}")
            element = page.locator(selector).first
            element.wait_for(state="visible", timeout=timeout)
            element.fill(value)
            print(f"[SMART_FILL] ✓ Заполнено: {name}")
            return True
        except Exception as e:
            print(f"[SMART_FILL] ✗ Селектор {i} не сработал: {e}")
            if i == len(selectors_list):
                print(f"[SMART_FILL] ⚠️ Все селекторы не сработали для: {name}")
                return False
    return False


def check_heading(page, expected_texts, timeout=5000):
    """
    Проверка наличия заголовка с альтернативными текстами

    Args:
        page: Playwright page
        expected_texts: Список альтернативных текстов заголовка
        timeout: Таймаут в миллисекундах

    Returns:
        True если заголовок найден, иначе False
    """
    for text in expected_texts:
        try:
            heading = page.get_by_role("heading", name=text)
            heading.wait_for(state="visible", timeout=timeout)
            print(f"[CHECK_HEADING] ✓ Найден заголовок: {text}")
            return True
        except:
            continue

    print(f"[CHECK_HEADING] ⚠️ Заголовок не найден из списка: {expected_texts}")
    return False


def wait_for_navigation(page, timeout=30000):
    """Ожидание завершения навигации"""
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
        print("[NAVIGATION] ✓ Страница загружена")
        return True
    except:
        print("[NAVIGATION] ⚠️ Таймаут навигации")
        return False


'''

    def _generate_csv_loader(self) -> str:
        return '''# ============================================================
# ЗАГРУЗКА CSV
# ============================================================

def load_csv_data() -> List[Dict]:
    """Загрузить данные из CSV"""
    if CSV_EMBED_MODE:
        return CSV_DATA
    else:
        data = []
        try:
            with open(CSV_FILENAME, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
        except Exception as e:
            print(f"[ERROR] Load CSV: {e}")
        return data


'''

    def _generate_main_iteration(self, user_code: str) -> str:
        return f'''# ============================================================
# ОСНОВНАЯ ФУНКЦИЯ ИТЕРАЦИИ
# ============================================================

def run_iteration(page, data_row: Dict, iteration_number: int):
    """
    Запуск одной итерации автоматизации

    Args:
        page: Playwright page
        data_row: Данные из CSV (Field 1, Field 2, ...)
        iteration_number: Номер итерации
    """
    print(f"\\n{'='*60}")
    print(f"[ITERATION {{iteration_number}}] Начало")
    print(f"{'='*60}")

    try:
{self._indent_code(user_code, 8)}

        print(f"[ITERATION {{iteration_number}}] ✓ Завершено успешно")
        return True

    except Exception as e:
        print(f"[ITERATION {{iteration_number}}] ✗ Ошибка: {{e}}")
        import traceback
        traceback.print_exc()
        return False


'''

    def _generate_main_function(self) -> str:
        return '''# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    """Главная функция запуска"""
    print("[MAIN] Запуск автоматизации...")

    # Загрузка CSV
    csv_data = load_csv_data()
    print(f"[MAIN] Загружено {len(csv_data)} строк данных")

    if not csv_data:
        print("[ERROR] Нет данных для обработки")
        return

    # Создание директории для профилей
    profiles_dir = Path("profiles")
    profiles_dir.mkdir(exist_ok=True)

    # Обработка каждой строки
    success_count = 0
    fail_count = 0

    for iteration_number, data_row in enumerate(csv_data, 1):
        print(f"\\n{'#'*60}")
        print(f"# ROW {iteration_number}/{len(csv_data)}")
        print(f"{'#'*60}")

        # Создание профиля для текущей итерации
        profile_path = profiles_dir / f"profile_{iteration_number}"
        profile_path.mkdir(exist_ok=True)

        print(f"[PROFILE] Путь: {profile_path}")

        try:
            with sync_playwright() as playwright:
                # Запуск браузера с persistent context
                browser = playwright.chromium.launch_persistent_context(
                    user_data_dir=str(profile_path),
                    headless=HEADLESS,
                    viewport=VIEWPORT,
                    args=[
                        "--no-sandbox",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-dev-shm-usage"
                    ]
                )

                page = browser.pages[0] if browser.pages else browser.new_page()
                page.set_default_timeout(DEFAULT_TIMEOUT)
                page.set_default_navigation_timeout(NAVIGATION_TIMEOUT)

                # Запуск итерации
                result = run_iteration(page, data_row, iteration_number)

                if result:
                    success_count += 1
                else:
                    fail_count += 1

                # Пауза перед закрытием
                time.sleep(2)

                browser.close()

        except Exception as e:
            print(f"[ERROR] Критическая ошибка в итерации {iteration_number}: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1

        # Пауза между итерациями
        if iteration_number < len(csv_data):
            print(f"[MAIN] Пауза 3 секунды перед следующей итерацией...")
            time.sleep(3)

    # Итоговая статистика
    print(f"\\n{'='*60}")
    print(f"[MAIN] ЗАВЕРШЕНО")
    print(f"[MAIN] Успешно: {success_count}/{len(csv_data)}")
    print(f"[MAIN] Ошибок: {fail_count}/{len(csv_data)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
'''

    def _indent_code(self, code: str, spaces: int) -> str:
        """Добавить отступы к коду"""
        indent = ' ' * spaces
        lines = code.split('\n')
        return '\n'.join(indent + line if line.strip() else '' for line in lines)
