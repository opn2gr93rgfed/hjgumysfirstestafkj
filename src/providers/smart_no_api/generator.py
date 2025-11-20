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
# Таймауты (оптимизированы для быстрого fail-over при неправильном флоу)
DEFAULT_TIMEOUT = 10000  # 10 секунд (было 30s, уменьшено для быстрых фейлов)
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

    ВАЖНО: Используется для подтверждения загрузки страницы/шага.
    Автоматически вызывается вместо page.get_by_role("heading").click()

    ФИЛОСОФИЯ: Heading проверки НЕ обязательны - сайты могут:
    - Показывать вопросы в разном порядке (A/B тесты)
    - Пропускать вопросы для определенных пользователей
    - Изменять текст заголовков динамически

    Если heading не найден - логируем WARNING и ПРОДОЛЖАЕМ выполнение.
    Exception бросаем только если ДЕЙСТВИЯ (click, fill) падают.

    Использует substring matching (exact=False), т.к. Playwright Recorder
    часто обрезает длинные заголовки до первых слов.

    Args:
        page: Playwright page
        expected_texts: Список альтернативных текстов заголовка (может быть строка или список)
        timeout: Таймаут в миллисекундах (по умолчанию 5 секунд - БЫСТРАЯ проверка)

    Returns:
        True если заголовок найден, False если не найден (не бросает exception!)
    """
    # Ensure expected_texts is a list
    if isinstance(expected_texts, str):
        expected_texts = [expected_texts]

    for text in expected_texts:
        try:
            # First try exact match
            heading = page.get_by_role("heading", name=text, exact=True)
            heading.wait_for(state="visible", timeout=timeout)
            print(f"[CHECK_HEADING] [OK] Найден заголовок (exact): {text}")
            # Small delay for page stability after heading appears
            time.sleep(0.5)
            return True
        except Exception as e:
            # If exact match failed, try substring match
            try:
                heading = page.get_by_role("heading", name=text, exact=False)
                heading.wait_for(state="visible", timeout=timeout)
                print(f"[CHECK_HEADING] [OK] Найден заголовок (partial): {text}")
                # Small delay for page stability after heading appears
                time.sleep(0.5)
                return True
            except:
                # Continue to next alternative
                continue

    # If no heading found, log warning but CONTINUE execution
    # This allows handling of dynamic flows, A/B tests, skipped questions, etc.
    print(f"[CHECK_HEADING] [WARNING] Заголовок не найден из списка: {expected_texts}")
    print(f"[CHECK_HEADING] [INFO] Это может быть нормально - сайт может показывать вопросы в разном порядке.")
    print(f"[CHECK_HEADING] [INFO] Продолжаем выполнение...")
    # Even if heading not found, give page a moment to stabilize
    time.sleep(0.3)
    return False


def safe_action(action_fn, description="action", critical=False):
    """
    Безопасное выполнение действия с обработкой ошибок

    ФИЛОСОФИЯ: Большинство действий НЕ критичны - если кнопка не найдена,
    возможно мы на другом шаге флоу. Продолжаем выполнение вместо остановки.

    Args:
        action_fn: Lambda функция с действием (например: lambda: page.click(...))
        description: Описание действия для логов
        critical: Если True - бросает exception при ошибке, если False - продолжает

    Returns:
        True если действие выполнено успешно, False если ошибка

    Example:
        safe_action(lambda: page.get_by_role("button", name="Next").click(), "Click Next button")
    """
    try:
        action_fn()
        print(f"[ACTION] [OK] {description}")
        return True
    except PlaywrightTimeout as e:
        print(f"[ACTION] [WARNING] Timeout: {description}")
        print(f"[ACTION] [INFO] Элемент не найден за отведенное время")
        print(f"[ACTION] [INFO] Возможно, мы на другом шаге флоу или вопрос пропущен")
        if critical:
            print(f"[ACTION] [ERROR] Это критичное действие - останавливаем выполнение")
            raise
        print(f"[ACTION] [INFO] Продолжаем выполнение следующих шагов...")
        # Small delay before continuing
        time.sleep(0.3)
        return False
    except Exception as e:
        print(f"[ACTION] [ERROR] Неожиданная ошибка: {description}")
        print(f"[ACTION] [ERROR] {str(e)[:200]}")
        if critical:
            raise
        print(f"[ACTION] [INFO] Продолжаем выполнение...")
        time.sleep(0.3)
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

        Трансформирует:
        - page.get_by_role("heading", name="...").click() → check_heading(page, ["..."])
        - Все page.* действия → обернуты в try-except для resilience

        ФИЛОСОФИЯ: Сайты с динамическими опросниками показывают вопросы в разном порядке.
        Действия должны продолжаться даже если элемент не найден - возможно другой вариант флоу.

        Оставляет только действия пользователя (page.goto, page.get_by_role, etc.)
        """
        import re

        # CRITICAL FIX: Normalize tabs to spaces BEFORE processing
        # This prevents TabError and IndentationError when user copies code with mixed tabs/spaces
        user_code = user_code.replace('\t', '    ')  # Replace all tabs with 4 spaces

        lines = user_code.split('\n')
        cleaned_lines = []
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

            # Transform heading clicks into check_heading() calls
            if 'get_by_role("heading"' in stripped or "get_by_role('heading'" in stripped:
                # Extract heading text using regex
                # Patterns: page.get_by_role("heading", name="TEXT").click()
                #           page.get_by_role('heading', name='TEXT').click()
                match = re.search(r'get_by_role\(["\']heading["\']\s*,\s*name=["\']([^"\']+)["\']', stripped)
                if match:
                    heading_text = match.group(1)
                    # Get current line indentation
                    current_indent = len(line) - len(line.lstrip())

                    # Remove base indentation if we're in run function
                    if in_run_function and base_indent is not None:
                        current_indent = max(0, current_indent - base_indent)

                    # Generate check_heading call with fast timeout (5s) for quick fail-over
                    transformed_line = ' ' * current_indent + f'check_heading(page, ["{heading_text}"], timeout=5000)'
                    cleaned_lines.append(transformed_line)
                    continue
                else:
                    # If we can't parse, skip the line (likely malformed)
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

        # Wrap all actions in resilient try-except blocks for dynamic flows
        return self._wrap_actions_for_resilience(cleaned_code)

    def _wrap_actions_for_resilience(self, code: str) -> str:
        """
        Обернуть все Playwright действия в try-except для resilience

        ФИЛОСОФИЯ: Динамические опросники меняют порядок вопросов каждый раз.
        Если кнопка/поле не найдено - это НОРМАЛЬНО, просто другой вариант флоу.
        Продолжаем выполнение вместо остановки.

        Оборачивает:
        - page.click()
        - page.fill()
        - page.get_by_*().click()/fill()
        - page.locator().click()/fill()
        - with page.expect_popup() (критично - НЕ оборачиваем)
        - page.goto() (критично - НЕ оборачиваем)
        """
        import re

        lines = code.split('\n')
        wrapped_lines = []
        i = 0
        inside_with_block = False
        with_block_indent = 0
        next_action_optional = False  # Track #optional marker
        current_page_context = 'page'  # Track current page context (page, page1, page2, page3)

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Check for #optional marker
            if stripped.lower() == '#optional':
                next_action_optional = True
                wrapped_lines.append(f"{' ' * (len(line) - len(line.lstrip()))}# Next action is optional (will not fail script if element not found)")
                i += 1
                continue

            # Skip empty lines and regular comments
            if not stripped or stripped.startswith('#'):
                wrapped_lines.append(line)
                i += 1
                continue

            # Get current indentation
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent

            # Track if we're inside a 'with' block (page, page1, page2, page3)
            if any(pattern in stripped for pattern in [
                'with page.expect_popup(',
                'with page.expect_navigation(',
                'with page1.expect_popup(',
                'with page1.expect_navigation(',
                'with page2.expect_popup(',
                'with page2.expect_navigation(',
                'with page3.expect_popup(',
                'with page3.expect_navigation(',
            ]):
                inside_with_block = True
                with_block_indent = indent

            # Fix indentation if code inside 'with' block has no indent (BEFORE checking exit!)
            # This MUST be done before "exited with block" check
            if inside_with_block and indent <= with_block_indent and stripped and not stripped.startswith('with'):
                # We're inside a with block but line has same/less indent - FIX IT
                # This happens when code is copy-pasted and loses indentation
                print(f"[GENERATOR] [WARNING] Fixed indentation inside 'with' block for: {stripped[:50]}")
                # Add 4 spaces indent - update the actual line
                line = ' ' * (with_block_indent + 4) + stripped
                stripped = line.strip()  # Keep stripped version updated
                indent = with_block_indent + 4  # Update indent for further processing
                indent_str = ' ' * indent
            elif inside_with_block and indent <= with_block_indent and not stripped.startswith('with'):
                # Only exit 'with' block if we didn't just fix indentation
                # and this is not the 'with' statement itself
                inside_with_block = False

            # Check if this is a critical action that should NOT be wrapped (must succeed)
            is_critical = any(pattern in stripped for pattern in [
                'page.goto(',
                'with page.expect_popup(',
                'with page.expect_navigation(',
                'check_heading(',  # Already has resilience built-in
                '= page',  # Variable assignments (page1 = ...)
                'wait_for_navigation(',
                'page1.',  # Actions on popup windows (page1, page2, etc.) - critical
                'page2.',
                'page3.',
            ])

            # Actions inside 'with' blocks are critical (must succeed to open popup/navigate)
            # BUT: if #optional marker was set, respect it even inside with blocks
            if inside_with_block and indent > with_block_indent and not next_action_optional:
                is_critical = True

            # If #optional marker was set, force this action to be non-critical
            # This check MUST come AFTER with-block check to override it
            if next_action_optional:
                is_critical = False
                next_action_optional = False  # Reset marker

            # Check if this is a resilient action (click, fill, etc.)
            is_action = any(pattern in stripped for pattern in [
                '.click(',
                '.fill(',
                '.select_option(',
                '.check(',
                '.uncheck(',
                '.set_checked(',
                '.press(',
                '.type(',
            ])

            # Check if this is a popup page action (page1/page2/page3) that needs retry logic
            is_popup_action = is_action and any(f'page{n}.' in stripped for n in [1, 2, 3])

            # Wrap action in try-except if it's resilient (not critical)
            if is_action and not is_critical:
                # Extract action description for logging (sanitize quotes)
                action_desc = self._extract_action_description(stripped)
                # Replace curly quotes for safe f-string usage in logs
                action_desc = action_desc.replace("'", "'").replace("'", "'").replace('"', '\\"')

                # IMPORTANT: Replace curly quotes in the actual code too!
                # Playwright Recorder can generate code with curly quotes like "Let's go"
                sanitized_code = stripped.replace("'", "'").replace("'", "'")

                wrapped_lines.append(f"{indent_str}try:")
                wrapped_lines.append(f"{indent_str}    {sanitized_code}")
                wrapped_lines.append(f"{indent_str}except PlaywrightTimeout:")
                wrapped_lines.append(f'{indent_str}    print(f"[ACTION] [WARNING] Timeout: {action_desc}")')
                wrapped_lines.append(f'{indent_str}    print(f"[ACTION] [INFO] Элемент не найден - возможно другой вариант флоу, продолжаем...")')
                wrapped_lines.append(f"{indent_str}    pass  # Continue execution")
            elif is_popup_action and is_critical:
                # Popup page actions need retry logic with extended timeout
                action_desc = self._extract_action_description(stripped)
                action_desc = action_desc.replace("'", "'").replace("'", "'").replace('"', '\\"')
                sanitized_code = stripped.replace("'", "'").replace("'", "'")

                # Extract page variable and selector for smart handling
                import re
                match = re.search(r'(page\d+)\.', stripped)
                page_var = match.group(1) if match else 'page1'

                # Extract selector information for element checking
                selector_match = re.search(r'\.get_by_\w+\([^)]+\)', stripped) or re.search(r'\.locator\([^)]+\)', stripped)
                has_selector = bool(selector_match)

                wrapped_lines.append(f"{indent_str}# Retry logic for popup page action with progressive delays and smart scrolling")
                wrapped_lines.append(f"{indent_str}max_retries = 5")
                wrapped_lines.append(f"{indent_str}progressive_delays = [5, 10, 15, 20, 30]  # Progressive delays in seconds")
                wrapped_lines.append(f"{indent_str}for retry_attempt in range(max_retries):")
                wrapped_lines.append(f"{indent_str}    try:")
                wrapped_lines.append(f"{indent_str}        if retry_attempt > 0:")
                wrapped_lines.append(f'{indent_str}            delay = progressive_delays[retry_attempt - 1]')
                wrapped_lines.append(f'{indent_str}            print(f"[POPUP_RETRY] Attempt {{retry_attempt+1}}/{{max_retries}} (waiting {{delay}}s): {action_desc}")')
                wrapped_lines.append(f"{indent_str}            time.sleep(delay)")
                wrapped_lines.append(f"{indent_str}            # Wait for page to stabilize")
                wrapped_lines.append(f"{indent_str}            {page_var}.wait_for_load_state('domcontentloaded', timeout=5000)")
                wrapped_lines.append(f"{indent_str}            # Scroll to bottom first to trigger lazy loading")
                wrapped_lines.append(f"{indent_str}            {page_var}.evaluate('window.scrollTo(0, document.body.scrollHeight)')")
                wrapped_lines.append(f"{indent_str}            time.sleep(0.5)")
                wrapped_lines.append(f"{indent_str}            # Scroll back to middle for element visibility")
                wrapped_lines.append(f"{indent_str}            {page_var}.evaluate('window.scrollTo(0, document.body.scrollHeight / 2)')")
                wrapped_lines.append(f"{indent_str}            time.sleep(0.3)")

                # Add scroll_into_view_if_needed for actions with selectors
                if has_selector and '.click()' in stripped:
                    # Extract the element locator part (everything before .click())
                    click_pos = stripped.find('.click()')
                    element_part = stripped[:click_pos].strip()
                    wrapped_lines.append(f"{indent_str}        # Scroll element into view if needed")
                    wrapped_lines.append(f"{indent_str}        try:")
                    wrapped_lines.append(f"{indent_str}            element = {element_part}")
                    wrapped_lines.append(f"{indent_str}            element.scroll_into_view_if_needed(timeout=3000)")
                    wrapped_lines.append(f"{indent_str}            time.sleep(0.2)  # Wait for scroll animation")
                    wrapped_lines.append(f'{indent_str}            print(f"[POPUP_ACTION] Element scrolled into view")')
                    wrapped_lines.append(f"{indent_str}        except:")
                    wrapped_lines.append(f'{indent_str}            print(f"[POPUP_ACTION] [WARNING] Could not scroll element into view, attempting anyway...")')
                    wrapped_lines.append(f"{indent_str}            pass")
                    # Replace original code with element.click() since we already have element
                    wrapped_lines.append(f"{indent_str}        element.click()")
                else:
                    wrapped_lines.append(f"{indent_str}        {sanitized_code}")

                wrapped_lines.append(f'{indent_str}        print(f"[POPUP_ACTION] [OK] {action_desc}")')
                wrapped_lines.append(f"{indent_str}        break  # Success - exit retry loop")
                wrapped_lines.append(f"{indent_str}    except PlaywrightTimeout:")
                wrapped_lines.append(f"{indent_str}        if retry_attempt == max_retries - 1:")
                wrapped_lines.append(f'{indent_str}            print(f"[POPUP_ACTION] [ERROR] Failed after {{max_retries}} attempts (total {{sum(progressive_delays)}}s): {action_desc}")')
                # Determine at generation time if this is an optional expandable button
                optional_keywords = ['show more', 'see more', 'load more', 'view more', 'expand', 'показать больше']
                action_lower = action_desc.lower()
                is_optional_button = any(keyword in action_lower for keyword in optional_keywords)

                if is_optional_button:
                    # Generate code that treats this as optional
                    wrapped_lines.append(f"{indent_str}            # Smart detection: This appears to be an optional expandable button")
                    wrapped_lines.append(f'{indent_str}            print(f"[POPUP_ACTION] [INFO] Button may not exist if content already loaded")')
                    wrapped_lines.append(f'{indent_str}            print(f"[POPUP_ACTION] [INFO] Checking page state...")')
                    wrapped_lines.append(f"{indent_str}            try:")
                    wrapped_lines.append(f"{indent_str}                {page_var}.wait_for_load_state('domcontentloaded', timeout=3000)")
                    wrapped_lines.append(f'{indent_str}                print(f"[POPUP_ACTION] [OK] Page stable - content likely already loaded, continuing...")')
                    wrapped_lines.append(f"{indent_str}            except:")
                    wrapped_lines.append(f'{indent_str}                print(f"[POPUP_ACTION] [WARNING] Page check failed but treating as optional")')
                    wrapped_lines.append(f"{indent_str}            break  # Continue execution without raising error")
                else:
                    # Generate code that treats this as critical
                    wrapped_lines.append(f"{indent_str}            raise  # Re-raise on final attempt for critical buttons")

                wrapped_lines.append(f"{indent_str}        else:")
                wrapped_lines.append(f'{indent_str}            print(f"[POPUP_RETRY] Timeout on attempt {{retry_attempt+1}}, retrying with longer delay...")')
                wrapped_lines.append(f"{indent_str}            continue")
            else:
                # Keep as-is (critical actions or non-actions)
                # But still sanitize curly quotes in critical code
                sanitized_line = line.replace("'", "'").replace("'", "'")

                # Check for special command comments (e.g., #pause10, #scrolldown)
                if stripped.startswith('#'):
                    command_handled = self._handle_special_command(stripped, indent_str, wrapped_lines, current_page_context)
                    if command_handled:
                        i += 1
                        continue

                wrapped_lines.append(sanitized_line)

                # If this is a popup page assignment, add scroll verification code
                # This helps verify page control and loads elements at the bottom
                if '= page1_info.value' in sanitized_line or '= page2_info.value' in sanitized_line or '= page3_info.value' in sanitized_line:
                    # Extract page variable name (page1, page2, etc.)
                    import re
                    match = re.search(r'(\w+)\s*=\s*page\d+_info\.value', sanitized_line)
                    if match:
                        page_var = match.group(1)
                        # Update current page context for special commands
                        current_page_context = page_var
                        wrapped_lines.append(f"{indent_str}# Wait for popup page to load and stabilize")
                        wrapped_lines.append(f"{indent_str}time.sleep(1.5)  # Extended wait for popup to fully load")
                        wrapped_lines.append(f"{indent_str}{page_var}.wait_for_load_state('domcontentloaded')")
                        wrapped_lines.append(f"{indent_str}try:")
                        wrapped_lines.append(f"{indent_str}    {page_var}.wait_for_load_state('networkidle', timeout=10000)")
                        wrapped_lines.append(f'{indent_str}    print(f"[POPUP] Network stabilized on {page_var}")')
                        wrapped_lines.append(f"{indent_str}except:")
                        wrapped_lines.append(f'{indent_str}    print(f"[POPUP] Network idle timeout - continuing anyway")')
                        wrapped_lines.append(f"{indent_str}    pass")
                        wrapped_lines.append(f"{indent_str}# Scroll down to load bottom elements (like 'See more')")
                        wrapped_lines.append(f"{indent_str}{page_var}.evaluate('window.scrollTo(0, document.body.scrollHeight)')")
                        wrapped_lines.append(f"{indent_str}time.sleep(0.5)")
                        wrapped_lines.append(f"{indent_str}# Scroll to middle position (50%) for element visibility")
                        wrapped_lines.append(f"{indent_str}{page_var}.evaluate('window.scrollTo(0, document.body.scrollHeight / 2)')")
                        wrapped_lines.append(f"{indent_str}time.sleep(0.3)")
                        wrapped_lines.append(f'{indent_str}print(f"[POPUP] [OK] {page_var} page loaded and scrolled to middle position")')
                        wrapped_lines.append(f'{indent_str}print(f"[POPUP] Elements at 50-75% position should now be visible")')

            i += 1

        return '\n'.join(wrapped_lines)

    def _handle_special_command(self, comment: str, indent_str: str, wrapped_lines: list, page_context: str = 'page') -> bool:
        """
        Обработать специальные команды в комментариях

        Поддерживаемые команды:
        - #pause5, #pause10, #pause20 - пауза N секунд
        - #scrolldown, #scroll - скролл вниз до конца страницы
        - #scrollup - скролл вверх к началу страницы
        - #scrollmid - скролл к середине страницы
        - #toggle_switches - переключить switches (снять первый checked, поставить первый unchecked)
        - #optional - следующее действие опционально (обернуть в try-except, даже если это page2)

        Args:
            page_context: Текущий контекст страницы (page, page1, page2, page3)

        Returns:
            True если команда обработана, False если это обычный комментарий
        """
        import re

        comment_lower = comment.lower().strip()

        # #pause5, #pause10, #pause20 - пауза N секунд
        pause_match = re.match(r'#pause(\d+)', comment_lower)
        if pause_match:
            seconds = pause_match.group(1)
            wrapped_lines.append(f"{indent_str}# User command: pause {seconds} seconds")
            wrapped_lines.append(f"{indent_str}print(f'[PAUSE] Waiting {seconds} seconds...')")
            wrapped_lines.append(f"{indent_str}time.sleep({seconds})")
            wrapped_lines.append(f"{indent_str}print(f'[PAUSE] Resume')")
            return True

        # #toggle_switches - переключить switches (первый checked -> uncheck, первый unchecked -> check)
        if comment_lower == '#toggle_switches':
            wrapped_lines.append(f"{indent_str}# User command: toggle switches")
            wrapped_lines.append(f"{indent_str}print(f'[SWITCHES] Toggling switches on {page_context}...')")
            wrapped_lines.append(f"{indent_str}try:")
            wrapped_lines.append(f"{indent_str}    # Find all switches on the page")
            wrapped_lines.append(f"{indent_str}    switches = {page_context}.get_by_role('switch').all()")
            wrapped_lines.append(f'{indent_str}    print(f"[SWITCHES] Found {{len(switches)}} switches")')
            wrapped_lines.append(f"{indent_str}    ")
            wrapped_lines.append(f"{indent_str}    # Find first checked switch and uncheck it")
            wrapped_lines.append(f"{indent_str}    for i, switch in enumerate(switches):")
            wrapped_lines.append(f"{indent_str}        if switch.is_checked():")
            wrapped_lines.append(f'{indent_str}            print(f"[SWITCHES] Unchecking switch {{i+1}} (was checked)")')
            wrapped_lines.append(f"{indent_str}            switch.uncheck()")
            wrapped_lines.append(f"{indent_str}            time.sleep(0.3)")
            wrapped_lines.append(f"{indent_str}            break")
            wrapped_lines.append(f"{indent_str}    ")
            wrapped_lines.append(f"{indent_str}    # Find first unchecked switch and check it")
            wrapped_lines.append(f"{indent_str}    for i, switch in enumerate(switches):")
            wrapped_lines.append(f"{indent_str}        if not switch.is_checked():")
            wrapped_lines.append(f'{indent_str}            print(f"[SWITCHES] Checking switch {{i+1}} (was unchecked)")')
            wrapped_lines.append(f"{indent_str}            switch.check()")
            wrapped_lines.append(f"{indent_str}            time.sleep(0.3)")
            wrapped_lines.append(f"{indent_str}            break")
            wrapped_lines.append(f"{indent_str}    ")
            wrapped_lines.append(f'{indent_str}    print(f"[SWITCHES] Switches toggled successfully")')
            wrapped_lines.append(f"{indent_str}except Exception as e:")
            wrapped_lines.append(f'{indent_str}    print(f"[SWITCHES] [ERROR] Failed to toggle switches: {{e}}")')
            return True

        # #optional - следующее действие опционально (будет обработано в основном коде)
        if comment_lower == '#optional':
            # This is a marker - will be handled in the main wrapping logic
            # Just preserve the comment for now
            return False

        # #scrolldown or #scroll - скролл вниз
        if comment_lower in ['#scrolldown', '#scroll']:
            wrapped_lines.append(f"{indent_str}# User command: scroll down")
            wrapped_lines.append(f"{indent_str}print(f'[SCROLL] Scrolling down on {page_context}...')")
            wrapped_lines.append(f"{indent_str}{page_context}.evaluate('window.scrollTo(0, document.body.scrollHeight)')")
            wrapped_lines.append(f"{indent_str}time.sleep(0.5)")
            return True

        # #scrollup - скролл вверх
        if comment_lower == '#scrollup':
            wrapped_lines.append(f"{indent_str}# User command: scroll up")
            wrapped_lines.append(f"{indent_str}print(f'[SCROLL] Scrolling up on {page_context}...')")
            wrapped_lines.append(f"{indent_str}{page_context}.evaluate('window.scrollTo(0, 0)')")
            wrapped_lines.append(f"{indent_str}time.sleep(0.5)")
            return True

        # #scrollmid - скролл к середине
        if comment_lower == '#scrollmid':
            wrapped_lines.append(f"{indent_str}# User command: scroll to middle")
            wrapped_lines.append(f"{indent_str}print(f'[SCROLL] Scrolling to middle on {page_context}...')")
            wrapped_lines.append(f"{indent_str}{page_context}.evaluate('window.scrollTo(0, document.body.scrollHeight / 2)')")
            wrapped_lines.append(f"{indent_str}time.sleep(0.5)")
            return True

        # Not a special command, just a regular comment
        return False

    def _extract_action_description(self, line: str) -> str:
        """Извлечь описание действия для логирования"""
        import re

        # Try to extract element description from various patterns

        # page.get_by_role("button", name="Next").click()
        match = re.search(r'get_by_role\(["\'](\w+)["\']\s*,\s*name=["\']([^"\']+)["\']', line)
        if match:
            role, name = match.groups()
            action = 'click' if '.click(' in line else 'fill' if '.fill(' in line else 'action'
            return f"{action} {role} '{name}'"

        # page.get_by_text("Continue").click()
        match = re.search(r'get_by_text\(["\']([^"\']+)["\']', line)
        if match:
            text = match.group(1)
            action = 'click' if '.click(' in line else 'action'
            return f"{action} text '{text}'"

        # page.get_by_placeholder("Enter name").fill(value)
        match = re.search(r'get_by_placeholder\(["\']([^"\']+)["\']', line)
        if match:
            placeholder = match.group(1)
            return f"fill placeholder '{placeholder}'"

        # page.locator("#id").click()
        match = re.search(r'locator\(["\']([^"\']+)["\']', line)
        if match:
            selector = match.group(1)
            action = 'click' if '.click(' in line else 'fill' if '.fill(' in line else 'action'
            return f"{action} '{selector}'"

        # Default: show the method being called
        if '.click(' in line:
            return "click element"
        elif '.fill(' in line:
            return "fill field"
        elif '.select_option(' in line:
            return "select option"
        elif '.check(' in line:
            return "check checkbox"

        return "action"

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
