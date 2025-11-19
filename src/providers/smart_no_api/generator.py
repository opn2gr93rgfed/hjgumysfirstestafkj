# SMART PROVIDER WITH OCTOBROWSER API + PROXY + FALLBACKS
"""
Provider: smart_no_api
Генератор скриптов с Octobrowser API, обязательными прокси и умными альтернативами
"""

import json
from typing import Dict, List


class Generator:
    """Генератор для Playwright через Octobrowser API с прокси"""

    def generate_script(self, user_code: str, config: Dict) -> str:
        """
        Генерирует Playwright скрипт с Octobrowser API + прокси

        Args:
            user_code: Код автоматизации из Playwright recorder
            config: Конфигурация (API token, proxy, profile settings)

        Returns:
            Полный исполняемый Python скрипт
        """
        api_token = config.get('api_token', '')
        csv_filename = config.get('csv_filename', 'data.csv')
        csv_data = config.get('csv_data', None)
        csv_embed_mode = config.get('csv_embed_mode', True)
        proxy_config = config.get('proxy', {})
        profile_config = config.get('profile', {})

        script = self._generate_imports()
        script += self._generate_config(api_token, csv_filename, csv_data, csv_embed_mode, proxy_config)
        script += self._generate_octobrowser_functions(profile_config, proxy_config)
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
Provider: smart_no_api (OCTOBROWSER API + PROXY + FALLBACKS)
"""

import csv
import time
import requests
from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeout
from typing import Dict, List, Optional

'''

    def _generate_config(self, api_token: str, csv_filename: str, csv_data: List[Dict],
                         csv_embed_mode: bool, proxy_config: Dict) -> str:
        config = f'''# ============================================================
# КОНФИГУРАЦИЯ
# ============================================================

# Octobrowser API
API_BASE_URL = "https://app.octobrowser.net/api/v2/automation"
API_TOKEN = "{api_token}"
LOCAL_API_URL = "http://localhost:58888/api"

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

        # Прокси конфигурация
        proxy_enabled = proxy_config.get('enabled', False)
        config += f'''# Прокси настройки (ОБЯЗАТЕЛЬНО)
USE_PROXY = {proxy_enabled}
'''

        if proxy_enabled:
            config += f'''PROXY_TYPE = "{proxy_config.get('type', 'http')}"
PROXY_HOST = "{proxy_config.get('host', '')}"
PROXY_PORT = "{proxy_config.get('port', '')}"
PROXY_LOGIN = "{proxy_config.get('login', '')}"
PROXY_PASSWORD = "{proxy_config.get('password', '')}"
'''

        config += '''
# Таймауты
DEFAULT_TIMEOUT = 30000  # 30 секунд
NAVIGATION_TIMEOUT = 60000  # 60 секунд

'''
        return config

    def _generate_octobrowser_functions(self, profile_config: Dict, proxy_config: Dict) -> str:
        """Генерирует функции Octobrowser API с поддержкой прокси"""
        if not profile_config:
            profile_config = {}

        fingerprint = profile_config.get('fingerprint') or {"os": "win"}
        tags = profile_config.get('tags', [])
        geolocation = profile_config.get('geolocation')

        fingerprint_json = json.dumps(fingerprint, ensure_ascii=False)
        tags_json = json.dumps(tags, ensure_ascii=False)
        geolocation_json = json.dumps(geolocation, ensure_ascii=False) if geolocation else 'None'

        return f'''# ============================================================
# OCTOBROWSER API ФУНКЦИИ
# ============================================================

def create_profile(title: str = "Auto Profile") -> Optional[str]:
    """Создать профиль через Octobrowser API с прокси"""
    url = f"{{API_BASE_URL}}/profiles"
    headers = {{"X-Octo-Api-Token": API_TOKEN}}

    profile_data = {{
        "title": title,
        "fingerprint": {fingerprint_json},
        "tags": {tags_json}
    }}

    # Добавление прокси если включено
    if USE_PROXY:
        profile_data["proxy"] = {{
            "type": PROXY_TYPE,
            "host": PROXY_HOST,
            "port": PROXY_PORT,
            "login": PROXY_LOGIN,
            "password": PROXY_PASSWORD
        }}
        print(f"[PROFILE] [!] ПРОКСИ ОБЯЗАТЕЛЕН: {{PROXY_TYPE}}://{{PROXY_HOST}}:{{PROXY_PORT}}")

    if {geolocation_json}:
        profile_data['geolocation'] = {geolocation_json}

    # Retry logic для rate limits и timeouts
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"[PROFILE] Отправка запроса на создание профиля (timeout=60s)...")
            response = requests.post(url, headers=headers, json=profile_data, timeout=60)
            print(f"[PROFILE] API Response Status: {{response.status_code}}")

            if response.status_code == 429:
                # Rate limit - retry with exponential backoff
                wait_time = 2 ** attempt * 5  # 5s, 10s, 20s
                print(f"[PROFILE] [!] Rate limit hit, waiting {{wait_time}}s before retry {{attempt+1}}/{{max_retries}}")
                time.sleep(wait_time)
                continue

            print(f"[PROFILE] API Response: {{response.text[:500]}}")

            if response.status_code in [200, 201]:
                result = response.json()
                if result.get('success') and 'data' in result:
                    profile_uuid = result['data']['uuid']
                    print(f"[PROFILE] [OK] Профиль создан: {{profile_uuid}}")
                    return profile_uuid
                else:
                    print(f"[PROFILE] [ERROR] Неожиданный формат ответа: {{result}}")
                    return None
            else:
                print(f"[PROFILE] [ERROR] Ошибка API: {{response.status_code}} - {{response.text}}")
                return None
        except requests.exceptions.Timeout:
            print(f"[PROFILE] [ERROR] Timeout при создании профиля (60s)")
            print(f"[PROFILE] [!] API не ответил вовремя, попытка {{attempt+1}}/{{max_retries}}")
            if attempt < max_retries - 1:
                wait_time = 5
                print(f"[PROFILE] Ожидание {{wait_time}}s перед повторной попыткой...")
                time.sleep(wait_time)
                continue
            else:
                print(f"[PROFILE] [ERROR] Все попытки исчерпаны")
                return None
        except (requests.exceptions.ConnectionError, ConnectionResetError) as e:
            print(f"[PROFILE] [ERROR] Соединение разорвано: {{str(e)[:100]}}")
            print(f"[PROFILE] [!] Возможные причины: прокси, перегрузка API, попытка {{attempt+1}}/{{max_retries}}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3  # 3s, 6s, 9s
                print(f"[PROFILE] Ожидание {{wait_time}}s перед повторной попыткой...")
                time.sleep(wait_time)
                continue
            else:
                print(f"[PROFILE] [ERROR] Все попытки исчерпаны после разрыва соединения")
                return None
        except Exception as e:
            print(f"[PROFILE] [ERROR] Exception при создании: {{e}}")
            import traceback
            traceback.print_exc()
            return None

    print(f"[PROFILE] [ERROR] Превышено число попыток создания профиля")
    return None


def check_local_api() -> bool:
    """Проверить доступность локального Octobrowser API"""
    try:
        print("[LOCAL_API] Проверка доступности локального Octobrowser...")
        response = requests.get(f"{{LOCAL_API_URL}}/profiles", timeout=5)
        if response.status_code in [200, 404]:  # 404 тоже OK - значит API работает
            print(f"[LOCAL_API] [OK] Локальный Octobrowser доступен на {{LOCAL_API_URL}}")
            return True
        else:
            print(f"[LOCAL_API] [ERROR] Неожиданный статус: {{response.status_code}}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[LOCAL_API] [ERROR] Не удалось подключиться к {{LOCAL_API_URL}}")
        print("[LOCAL_API] [!] Убедитесь, что Octobrowser запущен локально")
        return False
    except Exception as e:
        print(f"[LOCAL_API] [ERROR] Ошибка проверки: {{e}}")
        return False


def start_profile(profile_uuid: str) -> Optional[Dict]:
    """Запустить профиль и получить CDP endpoint"""
    url = f"{{LOCAL_API_URL}}/profiles/start"

    # Retry logic для синхронизации профиля с локальным Octobrowser
    max_retries = 8
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                wait_time = 2 ** (attempt - 1) * 2  # 0s, 2s, 4s, 8s, 16s
                print(f"[PROFILE] Ожидание синхронизации профиля: {{wait_time}}s")
                time.sleep(wait_time)

            print(f"[PROFILE] Попытка запуска {{attempt+1}}/{{max_retries}}: {{profile_uuid}}")

            # ============================================================
            # ⚠️ КРИТИЧЕСКИ ВАЖНО: ЕДИНСТВЕННО ПРАВИЛЬНЫЙ СПОСОБ ЗАПУСКА ПРОФИЛЯ!
            # ============================================================
            # Метод: POST (НЕ GET!)
            # URL: /profiles/start (НЕ /profiles/{{uuid}}/start!)
            # Body: JSON с uuid и параметрами
            #
            # ❌ НЕПРАВИЛЬНО: GET /profiles/{{uuid}}/start
            # ✅ ПРАВИЛЬНО: POST /profiles/start с body
            #
            # Это ПРОТЕСТИРОВАННЫЙ И РАБОТАЮЩИЙ способ!
            # Все остальные варианты НЕ работают и вызывают 404!
            # Используйте ТОЛЬКО этот пример во всех будущих провайдерах!
            # ============================================================
            response = requests.post(
                url,
                json={{
                    "uuid": profile_uuid,
                    "debug_port": True,
                    "headless": False,
                    "only_local": True,
                    "timeout": 120
                }},
                timeout=120
            )
            print(f"[PROFILE] Start Response Status: {{response.status_code}}")

            if response.status_code == 200:
                data = response.json()
                print(f"[PROFILE] [OK] Профиль запущен, CDP endpoint получен")
                return data
            elif response.status_code == 404:
                # Profile not synced yet - retry
                print(f"[PROFILE] [!] Профиль еще не синхронизирован с локальным Octobrowser")
                continue
            else:
                print(f"[PROFILE] [ERROR] Ошибка запуска: {{response.status_code}} - {{response.text}}")
                return None
        except Exception as e:
            print(f"[PROFILE] [ERROR] Exception при запуске: {{e}}")
            if attempt == max_retries - 1:
                import traceback
                traceback.print_exc()
            continue

    print(f"[PROFILE] [ERROR] Не удалось запустить профиль после {{max_retries}} попыток")
    print(f"[PROFILE] [!] Убедитесь что Octobrowser запущен локально (http://localhost:58888)")
    return None


def stop_profile(profile_uuid: str):
    """Остановить профиль"""
    url = f"{{LOCAL_API_URL}}/profiles/{{profile_uuid}}/stop"
    try:
        requests.get(url, timeout=10)
        print(f"[PROFILE] [OK] Профиль остановлен")
    except Exception as e:
        print(f"[PROFILE] [!] Не удалось остановить: {{e}}")


def delete_profile(profile_uuid: str):
    """Удалить профиль"""
    url = f"{{API_BASE_URL}}/profiles/{{profile_uuid}}"
    headers = {{"X-Octo-Api-Token": API_TOKEN}}
    try:
        requests.delete(url, headers=headers, timeout=10)
        print(f"[PROFILE] [OK] Профиль удалён")
    except Exception as e:
        print(f"[PROFILE] [!] Не удалось удалить: {{e}}")


'''

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
            print(f"[SMART_CLICK] [OK] Клик выполнен: {name}")
            return True
        except Exception as e:
            print(f"[SMART_CLICK] [ERROR] Селектор {i} не сработал: {e}")
            if i == len(selectors_list):
                print(f"[SMART_CLICK] [!] Все селекторы не сработали для: {name}")
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
            print(f"[SMART_FILL] [OK] Заполнено: {name}")
            return True
        except Exception as e:
            print(f"[SMART_FILL] [ERROR] Селектор {i} не сработал: {e}")
            if i == len(selectors_list):
                print(f"[SMART_FILL] [!] Все селекторы не сработали для: {name}")
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
            print(f"[CHECK_HEADING] [OK] Найден заголовок: {text}")
            return True
        except:
            continue

    print(f"[CHECK_HEADING] [!] Заголовок не найден из списка: {expected_texts}")
    return False


def wait_for_navigation(page, timeout=30000):
    """Ожидание завершения навигации"""
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
        print("[NAVIGATION] [OK] Страница загружена")
        return True
    except:
        print("[NAVIGATION] [!] Таймаут навигации")
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

    def _clean_user_code(self, user_code: str) -> str:
        """
        Очистить пользовательский код от boilerplate Playwright Recorder

        Удаляет:
        - import statements
        - def run(playwright) wrapper
        - browser.launch(), context, page creation
        - browser.close(), context.close()
        - with sync_playwright() wrapper

        Оставляет только действия пользователя (page.goto, page.get_by_role, etc.)
        """
        lines = user_code.split('\n')
        cleaned_lines = []
        skip_until_def_end = False
        in_run_function = False
        base_indent = None

        for line in lines:
            stripped = line.strip()

            # Skip empty lines and comments at start
            if not stripped or stripped.startswith('#'):
                continue

            # Skip imports
            if stripped.startswith('import ') or stripped.startswith('from '):
                continue

            # Skip def run(playwright) line
            if 'def run(' in stripped and 'playwright' in stripped:
                in_run_function = True
                continue

            # Skip browser/context/page setup
            if any(pattern in stripped for pattern in [
                'browser = playwright.chromium.launch',
                'context = browser.new_context',
                'page = context.new_page',
                'browser.launch(',
                'new_context(',
                'new_page('
            ]):
                continue

            # Skip browser/context close
            if any(pattern in stripped for pattern in [
                'context.close()',
                'browser.close()',
                '.close()'
            ]) and 'page' not in stripped:
                continue

            # Skip with sync_playwright wrapper
            if 'with sync_playwright()' in stripped:
                continue
            if stripped == 'run(playwright)':
                continue

            # Skip separator comments
            if stripped.startswith('# -----'):
                continue

            # If we're in run function, adjust indentation
            if in_run_function and stripped:
                # Detect base indentation from first real action
                if base_indent is None and not stripped.startswith('def '):
                    base_indent = len(line) - len(line.lstrip())

                # Remove base indentation
                if base_indent is not None:
                    if line.startswith(' ' * base_indent):
                        cleaned_line = line[base_indent:]
                        cleaned_lines.append(cleaned_line)
                    else:
                        # Line with less indentation - keep as is
                        cleaned_lines.append(line.lstrip())

        cleaned_code = '\n'.join(cleaned_lines)

        # If we couldn't extract anything, return original code
        # (maybe it's already clean or in different format)
        if not cleaned_code.strip():
            return user_code

        return cleaned_code

    def _generate_main_iteration(self, user_code: str) -> str:
        # Clean user code from Playwright Recorder boilerplate
        cleaned_code = self._clean_user_code(user_code)

        return f'''# ============================================================
# ОСНОВНАЯ ФУНКЦИЯ ИТЕРАЦИИ
# ============================================================

def run_iteration(page, data_row: Dict, iteration_number: int):
    """
    Запуск одной итерации автоматизации

    Args:
        page: Playwright page (уже подключен к Octobrowser через CDP)
        data_row: Данные из CSV (Field 1, Field 2, ...)
        iteration_number: Номер итерации
    """
    print(f"\\n{'='*60}")
    print(f"[ITERATION {{iteration_number}}] Начало")
    print(f"{'='*60}")

    try:
        # ============================================================
        # ДЕЙСТВИЯ ПОЛЬЗОВАТЕЛЯ (очищены от Playwright boilerplate)
        # ============================================================
{self._indent_code(cleaned_code, 8)}

        print(f"[ITERATION {{iteration_number}}] [OK] Завершено успешно")
        return True

    except Exception as e:
        print(f"[ITERATION {{iteration_number}}] [ERROR] Ошибка: {{e}}")
        import traceback
        traceback.print_exc()
        return False


'''

    def _generate_main_function(self) -> str:
        return '''# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    """Главная функция запуска через Octobrowser API"""
    print("[MAIN] Запуск автоматизации через Octobrowser API...")
    print(f"[MAIN] API Token: {API_TOKEN[:10]}..." if API_TOKEN else "[MAIN] [!] API Token отсутствует!")

    if USE_PROXY:
        print(f"[MAIN] [OK] ПРОКСИ ВКЛЮЧЕН: {PROXY_TYPE}://{PROXY_HOST}:{PROXY_PORT}")
    else:
        print("[MAIN] [!] ПРОКСИ НЕ ВКЛЮЧЕН!")

    # Проверка доступности локального Octobrowser
    if not check_local_api():
        print("[MAIN] [ERROR] Локальный Octobrowser недоступен!")
        print("[MAIN] [!] Запустите Octobrowser и убедитесь, что он работает на http://localhost:58888")
        return

    # Загрузка CSV
    csv_data = load_csv_data()
    print(f"[MAIN] Загружено {len(csv_data)} строк данных")

    if not csv_data:
        print("[ERROR] Нет данных для обработки")
        return

    # Обработка каждой строки
    success_count = 0
    fail_count = 0

    for iteration_number, data_row in enumerate(csv_data, 1):
        print(f"\\n{'#'*60}")
        print(f"# ROW {iteration_number}/{len(csv_data)}")
        print(f"{'#'*60}")

        # Задержка между итерациями для предотвращения перегрузки API
        if iteration_number > 1:
            wait_time = 2
            print(f"[API] Задержка {wait_time}s перед созданием следующего профиля...")
            time.sleep(wait_time)

        profile_uuid = None

        try:
            # Создание профиля через API
            profile_title = f"Auto Profile {iteration_number}"
            print(f"[PROFILE] Создание профиля: {profile_title}")
            profile_uuid = create_profile(profile_title)

            if not profile_uuid:
                print("[ERROR] Не удалось создать профиль")
                fail_count += 1
                continue

            print(f"[PROFILE] UUID: {profile_uuid}")

            # Ожидание синхронизации профиля с локальным Octobrowser
            print("[PROFILE] Ожидание синхронизации с локальным Octobrowser (5 сек)...")
            time.sleep(5)

            # Запуск профиля
            print("[PROFILE] Запуск...")
            start_data = start_profile(profile_uuid)

            if not start_data:
                print("[ERROR] Не удалось запустить профиль")
                fail_count += 1
                continue

            debug_url = start_data.get('ws_endpoint')
            if not debug_url:
                print("[ERROR] Нет CDP endpoint")
                fail_count += 1
                continue

            print(f"[PROFILE] [OK] CDP endpoint получен")

            # Подключение через Playwright CDP
            with sync_playwright() as playwright:
                browser = playwright.chromium.connect_over_cdp(debug_url)
                context = browser.contexts[0]
                page = context.pages[0]

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

            print(f"[PROFILE] Остановка профиля")
            stop_profile(profile_uuid)

        except Exception as e:
            print(f"[ERROR] Критическая ошибка в итерации {iteration_number}: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1

        finally:
            if profile_uuid:
                time.sleep(1)

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
