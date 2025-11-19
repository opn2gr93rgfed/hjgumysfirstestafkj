"""
Генератор Playwright скриптов для автоматизации с Octobrowser
"""

import json
from typing import Dict, List


class PlaywrightScriptGenerator:
    """Генератор Playwright скриптов"""

    def generate_script(self, user_code: str, config: Dict) -> str:
        """
        Генерирует полный Playwright скрипт

        Args:
            user_code: Пользовательский код автоматизации
            config: Конфигурация (API token, proxy, sms, target, etc.)

        Returns:
            Полный исполняемый Python скрипт
        """
        # Извлечь настройки
        api_token = config.get('api_token', '')
        use_proxy = config.get('use_proxy', False)
        proxy_config = config.get('proxy', {})
        csv_filename = config.get('csv_filename', 'data.csv')
        csv_data = config.get('csv_data', None)  # 🔥 Встроенные CSV данные
        csv_embed_mode = config.get('csv_embed_mode', True)  # 🔥 Режим встраивания
        use_sms = config.get('use_sms', False)
        sms_config = config.get('sms', {})
        target = config.get('target', 'library')  # library или cdp
        profile_config = config.get('profile', {})  # 🔥 НАСТРОЙКИ ПРОФИЛЯ ИЗ GUI

        # Генерация скрипта
        script = self._generate_imports()
        script += self._generate_config(api_token, proxy_config, use_proxy, csv_filename, csv_data, csv_embed_mode, use_sms, sms_config, target)

        # Добавить функции Octobrowser (всегда нужны для CDP подключения)
        # 🔥 ПЕРЕДАЁМ НАСТРОЙКИ ПРОФИЛЯ В ГЕНЕРАТОР
        script += self._generate_octobrowser_functions(profile_config)

        # Добавить SMS функции если включено
        if use_sms:
            script += self._generate_sms_functions(sms_config)

        script += self._generate_csv_loader(use_sms)
        script += self._generate_main_iteration(user_code, use_sms, target)
        script += self._generate_main_function()

        return script

    def _generate_imports(self) -> str:
        """Генерирует импорты"""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматически сгенерированный скрипт автоматизации
Фреймворк: Playwright (SYNC API)
Браузер: Octobrowser (через CDP)
"""

import csv
import time
import random
import requests
from playwright.sync_api import sync_playwright, Playwright, expect
from typing import Dict, List, Optional

'''

    def _generate_config(self, api_token: str, proxy_config: Dict, use_proxy: bool,
                         csv_filename: str, csv_data: List[Dict], csv_embed_mode: bool,
                         use_sms: bool, sms_config: Dict, target: str) -> str:
        """Генерирует конфигурацию"""
        config = f'''# ============================================================
# КОНФИГУРАЦИЯ
# ============================================================

# Playwright target (формат импортированного скрипта)
PLAYWRIGHT_TARGET = "{target}"  # library или cdp (только для справки, не влияет на выполнение)

# Octobrowser API
API_BASE_URL = "https://app.octobrowser.net/api/v2/automation"
API_TOKEN = "{api_token}"
LOCAL_API_URL = "http://localhost:58888/api"

'''

        # 🔥 КРЕАТИВНОЕ РЕШЕНИЕ: Встроенные CSV данные или путь к файлу
        if csv_embed_mode and csv_data:
            # Встроить CSV данные прямо в скрипт
            import json
            config += f'''# 🔥 CSV данные (встроены в скрипт)
CSV_EMBED_MODE = True
CSV_DATA = {json.dumps(csv_data, ensure_ascii=False, indent=2)}

'''
        else:
            # Использовать путь к файлу
            config += f'''# CSV файл с данными
CSV_EMBED_MODE = False
CSV_FILENAME = "{csv_filename}"

'''

        config += f'''# Прокси настройки
USE_PROXY = {use_proxy}
'''

        if use_proxy:
            config += f'''PROXY_TYPE = "{proxy_config.get('type', 'http')}"
PROXY_HOST = "{proxy_config.get('host', '')}"
PROXY_PORT = "{proxy_config.get('port', '')}"
PROXY_LOGIN = "{proxy_config.get('login', '')}"
PROXY_PASSWORD = "{proxy_config.get('password', '')}"
'''

        # SMS настройки
        config += f'''
# SMS провайдер для получения номеров и OTP
USE_SMS_PROVIDER = {use_sms}
'''

        if use_sms:
            sms_provider = sms_config.get('provider', 'daisysms')
            sms_api_key = sms_config.get('api_key', '')
            sms_service = sms_config.get('service', 'ds')

            config += f'''SMS_PROVIDER = "{sms_provider}"
SMS_API_KEY = "{sms_api_key}"
SMS_SERVICE = "{sms_service}"  # ds=Discord, go=Google, wa=WhatsApp, tg=Telegram
SMS_API_BASE_URL = "https://daisysms.com/stubs/handler_api.php"
'''

        config += '\n\n'
        return config

    def _generate_octobrowser_functions(self, profile_config: Dict = None) -> str:
        """Генерирует функции работы с Octobrowser API"""
        if profile_config is None:
            profile_config = {}

        # Подготовить значения из конфигурации (ДО f-string чтобы избежать unhashable type error)
        import json

        fingerprint = profile_config.get('fingerprint') or {"os": "win"}
        tags = profile_config.get('tags', [])
        notes = profile_config.get('notes', '')
        geolocation = profile_config.get('geolocation')

        # Конвертировать в JSON строки для вставки в код
        fingerprint_json = json.dumps(fingerprint)
        tags_json = json.dumps(tags)
        notes_repr = repr(notes)
        geolocation_json = json.dumps(geolocation) if geolocation else "None"

        return f'''# ============================================================
# ФУНКЦИИ OCTOBROWSER API
# ============================================================

def create_profile() -> Optional[str]:
    """Создание профиля через Octobrowser API"""
    url = f"{{API_BASE_URL}}/profiles"
    # 🔥 ПРАВИЛЬНЫЙ заголовок согласно официальной документации
    # https://docs.octobrowser.net/
    # > All requests require authentication via API token in the X-Octo-Api-Token header
    headers = {{"X-Octo-Api-Token": API_TOKEN}}

    # 🔥 НАСТРОЙКИ ПРОФИЛЯ ИЗ GUI (Octo API Tab)
    profile_data = {{
        "title": f"AutoProfile_{{int(time.time())}}",
        "fingerprint": {fingerprint_json},
    }}

    # Добавить теги если указаны
    tags = {tags_json}
    if tags:
        profile_data["tags"] = tags
        print(f"[TAGS] Установлены теги: {{tags}}")

    # Добавить заметки если указаны
    notes = {notes_repr}
    if notes:
        profile_data["notes"] = notes

    # Добавить geolocation если включено
    geolocation = {geolocation_json}
    if geolocation:
        profile_data["geolocation"] = geolocation
        print(f"[GEO] Установлена геолокация: {{geolocation.get('latitude')}}, {{geolocation.get('longitude')}}")

    # Добавить прокси если включено
    if USE_PROXY:
        profile_data["proxy"] = {{
            "type": PROXY_TYPE,
            "host": PROXY_HOST,
            "port": PROXY_PORT,
            "login": PROXY_LOGIN,
            "password": PROXY_PASSWORD
        }}
        print(f"[PROXY] Установлен прокси: {{PROXY_TYPE}}://{{PROXY_HOST}}:{{PROXY_PORT}}")

    try:
        response = requests.post(url, headers=headers, json=profile_data)
        response.raise_for_status()
        result = response.json()

        if result.get('success') and 'data' in result:
            profile_uuid = result['data']['uuid']
            print(f"[OK] Профиль создан: {{profile_uuid}}")
            return profile_uuid
        else:
            print(f"[ERROR] Не удалось создать профиль: {{result}}")
            return None

    except Exception as e:
        print(f"[ERROR] Ошибка создания профиля: {{e}}")
        return None


def start_profile(profile_uuid: str) -> Optional[str]:
    """Запуск профиля через локальный API"""
    url = f"{{LOCAL_API_URL}}/profiles/start"
    payload = {{
        "uuid": profile_uuid,
        "headless": False,
        "debug_port": True
    }}

    try:
        print(f"Запуск профиля {{profile_uuid}}...")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()

        debug_port = result.get('debug_port')
        if debug_port:
            print(f"[OK] Профиль запущен на порту: {{debug_port}}")
            # Подождать инициализации
            time.sleep(3)
            return str(debug_port)
        else:
            print(f"[ERROR] Не получен debug_port: {{result}}")
            return None

    except Exception as e:
        print(f"[ERROR] Ошибка запуска профиля: {{e}}")
        return None


def stop_profile(profile_uuid: str) -> bool:
    """Остановка профиля"""
    url = f"{{LOCAL_API_URL}}/profiles/stop"
    payload = {{"uuid": profile_uuid}}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"[OK] Профиль {{profile_uuid}} остановлен")
        return True
    except Exception as e:
        print(f"[WARNING] Не удалось остановить профиль: {{e}}")
        return False


def check_local_api() -> bool:
    """
    Проверить доступность локального API Octobrowser

    ВАЖНО: Octobrowser desktop приложение ДОЛЖНО БЫТЬ ЗАПУЩЕНО для работы Local API!
    Без запущенного Octobrowser профили не смогут открыться.

    Returns:
        bool: True если Local API доступен, False если нет
    """
    try:
        print("[CHECK] Проверка доступности Octobrowser Local API...")
        response = requests.get(f"{{LOCAL_API_URL}}/profiles", timeout=2)

        if response.status_code in [200, 401, 403]:  # Любой ответ = API работает
            print("[OK] Local API доступен (Octobrowser запущен)")
            return True
        else:
            print(f"[WARNING] Local API вернул неожиданный статус: {{response.status_code}}")
            return True  # Всё равно API работает, пусть попробует

    except requests.exceptions.ConnectionError:
        print("\\n" + "="*60)
        print("[CRITICAL ERROR] OCTOBROWSER НЕ ЗАПУЩЕН!")
        print("="*60)
        print("")
        print("Local API недоступен на http://localhost:58888/api")
        print("")
        print("РЕШЕНИЕ:")
        print("1. Запустите приложение Octobrowser на вашем компьютере")
        print("2. Убедитесь, что Octobrowser работает")
        print("3. Запустите этот скрипт снова")
        print("")
        print("СПРАВКА:")
        print("- Cloud API (создание профилей) работает через интернет")
        print("- Local API (запуск профилей) требует запущенного Octobrowser")
        print("- Без Local API профили будут создаваться, но НЕ запускаться")
        print("")
        print("="*60 + "\\n")
        return False

    except requests.exceptions.Timeout:
        print("[ERROR] Timeout при проверке Local API (превышено время ожидания)")
        print("Octobrowser может быть запущен, но не отвечает")
        return False

    except Exception as e:
        print(f"[ERROR] Ошибка проверки Local API: {{e}}")
        return False


'''

    def _generate_sms_functions(self, sms_config: Dict) -> str:
        """Генерирует функции для работы с SMS API"""
        return '''# ============================================================
# ФУНКЦИИ SMS ПРОВАЙДЕРА (DaisySMS)
# ============================================================

def get_phone_number() -> Optional[Dict]:
    """
    Получить номер телефона от SMS провайдера

    Returns:
        Dict: {'activation_id': str, 'phone_number': str} или None
    """
    url = SMS_API_BASE_URL
    params = {
        'api_key': SMS_API_KEY,
        'action': 'getNumber',
        'service': SMS_SERVICE
    }

    try:
        print(f"[SMS] Запрос номера: service={SMS_SERVICE}")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        result = response.text.strip()

        print(f"[SMS] Ответ API: {result}")

        # Формат: ACCESS_NUMBER:ID:PHONE_NUMBER
        if result.startswith('ACCESS_NUMBER:'):
            parts = result.split(':')
            activation_id = parts[1]
            phone_number = parts[2]

            print(f"[SMS] [OK] Получен номер: {phone_number} (ID: {activation_id})")
            return {
                'activation_id': activation_id,
                'phone_number': phone_number
            }
        else:
            # Детальное логирование ошибок от API
            error_messages = {
                'NO_NUMBERS': 'Нет доступных номеров для данного сервиса',
                'NO_BALANCE': 'Недостаточно средств на балансе',
                'BAD_ACTION': 'Неверное действие (проверьте параметры)',
                'BAD_SERVICE': 'Неверный код сервиса',
                'BAD_KEY': 'Неверный API ключ',
                'ERROR_SQL': 'Ошибка на стороне сервера'
            }
            error_msg = error_messages.get(result, f"Неизвестная ошибка: {result}")
            print(f"[SMS ERROR] {error_msg}")
            return None

    except Exception as e:
        print(f"[SMS ERROR] Ошибка запроса к API: {e}")
        return None


def get_phone_number_with_retry(max_retries=5) -> Optional[Dict]:
    """
    Получить номер с УМНОЙ retry логикой и экспоненциальной задержкой

    Реализует Enterprise Pattern: Retry with Exponential Backoff

    Args:
        max_retries: Максимальное количество попыток (по умолчанию 5)

    Returns:
        Dict с номером или None после всех попыток
    """
    print(f"[SMS RETRY] Начинаем получение номера (макс. {max_retries} попыток)")

    for attempt in range(1, max_retries + 1):
        print(f"[SMS RETRY] === Попытка {attempt}/{max_retries} ===")

        sms_data = get_phone_number()

        if sms_data:
            print(f"[SMS RETRY] [SUCCESS] УСПЕХ на попытке {attempt}!")
            return sms_data

        # Если не последняя попытка - ждем перед повтором
        if attempt < max_retries:
            # Экспоненциальная задержка: 2, 4, 8, 16, 32 секунды
            wait_time = 2 ** attempt
            print(f"[SMS RETRY] [WAIT] Ожидание {wait_time} секунд перед следующей попыткой...")
            time.sleep(wait_time)

    print(f"[SMS RETRY] [FAIL] ПРОВАЛ: Не удалось получить номер после {max_retries} попыток")
    return None


def get_sms_code(activation_id: str, timeout: int = 180) -> Optional[str]:
    """
    Получить SMS код (OTP)

    Args:
        activation_id: ID активации от get_phone_number
        timeout: Максимальное время ожидания в секундах

    Returns:
        str: OTP код или None
    """
    url = SMS_API_BASE_URL
    start_time = time.time()
    poll_interval = 3  # Минимум 3 секунды между запросами

    print(f"[SMS] Ожидание SMS кода (макс. {timeout}s)...")

    while (time.time() - start_time) < timeout:
        params = {
            'api_key': SMS_API_KEY,
            'action': 'getStatus',
            'id': activation_id
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            result = response.text.strip()

            # STATUS_OK:CODE - SMS получено
            if result.startswith('STATUS_OK:'):
                code = result.split(':')[1]
                print(f"[SMS] [OK] Получен OTP код: {code}")
                return code

            # STATUS_WAIT_CODE - ожидание
            elif result == 'STATUS_WAIT_CODE':
                elapsed = int(time.time() - start_time)
                print(f"[SMS] Ожидание... ({elapsed}s/{timeout}s)")
                time.sleep(poll_interval)
                continue

            # STATUS_CANCEL - отменено
            elif result == 'STATUS_CANCEL':
                print(f"[SMS ERROR] Активация отменена")
                return None

            # NO_ACTIVATION - неверный ID
            elif result == 'NO_ACTIVATION':
                print(f"[SMS ERROR] Активация не найдена")
                return None

            else:
                print(f"[SMS] Статус: {result}")
                time.sleep(poll_interval)

        except Exception as e:
            print(f"[SMS ERROR] Ошибка запроса: {e}")
            time.sleep(poll_interval)

    print(f"[SMS ERROR] Превышено время ожидания ({timeout}s)")
    return None


def cancel_sms_activation(activation_id: str) -> bool:
    """Отменить SMS активацию"""
    url = SMS_API_BASE_URL
    params = {
        'api_key': SMS_API_KEY,
        'action': 'setStatus',
        'id': activation_id,
        'status': 8  # 8 = отмена
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        result = response.text.strip()

        if result == 'ACCESS_CANCEL':
            print(f"[SMS] Активация {activation_id} отменена")
            return True
        else:
            print(f"[SMS ERROR] Не удалось отменить: {result}")
            return False

    except Exception as e:
        print(f"[SMS ERROR] Ошибка отмены: {e}")
        return False


'''

    def _generate_csv_loader(self, use_sms: bool = False) -> str:
        """Генерирует функцию загрузки CSV"""
        return '''# ============================================================
# ЗАГРУЗКА ДАННЫХ ИЗ CSV
# ============================================================

def load_data_from_csv(filename: str = None) -> List[Dict]:
    """
    Загружает данные из CSV файла или использует встроенные данные

    🔥 КРЕАТИВНОЕ РЕШЕНИЕ:
    - Если CSV_EMBED_MODE=True, использует встроенные CSV_DATA
    - Если CSV_EMBED_MODE=False, читает файл CSV_FILENAME
    """
    try:
        # 🔥 Режим 1: Встроенные данные (CSV уже в скрипте)
        if CSV_EMBED_MODE:
            data_rows = CSV_DATA
            print(f"[OK] Используются встроенные CSV данные")
            print(f"Загружено {len(data_rows)} строк данных")
            return data_rows

        # 🔥 Режим 2: Чтение из файла (классический способ)
        if filename is None:
            filename = CSV_FILENAME

        data_rows = []
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data_rows.append(row)

        print(f"[OK] CSV файл найден: {filename}")
        print(f"Загружено {len(data_rows)} строк данных")
        return data_rows

    except FileNotFoundError:
        print(f"[ERROR] CSV файл не найден: {filename}")
        print("Создайте CSV файл с данными перед запуском!")
        return []
    except Exception as e:
        print(f"[ERROR] Ошибка чтения CSV: {e}")
        return []


def update_csv_row(filename: str = None, row_index: int = 0, phone_number: Optional[str] = None, otp_code: Optional[str] = None):
    """
    Обновить строку CSV файла с реальными значениями phone_number и otp_code

    🔥 КРЕАТИВНОЕ РЕШЕНИЕ:
    - Если CSV_EMBED_MODE=True, пропускает обновление (данные встроены)
    - Если CSV_EMBED_MODE=False, обновляет файл

    Args:
        filename: Имя CSV файла
        row_index: Индекс строки (начиная с 0)
        phone_number: Новое значение для колонки phone_number
        otp_code: Новое значение для колонки otp_code
    """
    try:
        # 🔥 Режим 1: Встроенные данные - обновление невозможно
        if CSV_EMBED_MODE:
            print(f"[CSV] Режим встроенных данных - запись в CSV пропущена")
            return
        # Читаем весь CSV
        rows = []
        fieldnames = []
        with open(filename, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
            for row in reader:
                rows.append(row)

        if not rows:
            print(f"[CSV WARNING] Файл пустой: {filename}")
            return

        if row_index < 0 or row_index >= len(rows):
            print(f"[CSV WARNING] Неверный индекс строки: {row_index}")
            return

        # Обновляем значения в строке
        updated = False
        if phone_number is not None:
            rows[row_index]['phone_number'] = phone_number
            updated = True
            print(f"[CSV] Обновлено: строка {row_index + 1}, phone_number = {phone_number}")

        if otp_code is not None:
            rows[row_index]['otp_code'] = otp_code
            updated = True
            print(f"[CSV] Обновлено: строка {row_index + 1}, otp_code = {otp_code}")

        # Записываем обратно в файл
        if updated:
            with open(filename, 'w', encoding='utf-8', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            print(f"[CSV] [OK] Файл обновлен: {filename}")

    except FileNotFoundError:
        print(f"[CSV ERROR] Файл не найден: {filename}")
    except Exception as e:
        print(f"[CSV ERROR] Ошибка обновления CSV: {e}")


'''

    def _generate_main_iteration(self, user_code: str, use_sms: bool = False, target: str = 'library') -> str:
        """Генерирует главную функцию итерации"""
        # 🔥 ИСПРАВЛЕНИЕ: Сначала убрать общий отступ из user_code, потом добавить нужный (12 пробелов)
        import textwrap
        dedented_code = textwrap.dedent(user_code)  # Убрать общий отступ
        indented_code = '\n'.join(' ' * 12 + line if line.strip() else ''
                                  for line in dedented_code.split('\n'))

        # Добавить SMS блок если включено
        sms_block = ''
        if use_sms:
            sms_block = '''
        # ============================================================
        # ПОЛУЧЕНИЕ НОМЕРА С УМНОЙ RETRY ЛОГИКОЙ (Fail-Fast Pattern)
        # ============================================================

        sms_activation_id = None

        if USE_SMS_PROVIDER:
            print("[SMS] === НАЧИНАЕМ ПОЛУЧЕНИЕ НОМЕРА ===")

            # Получить номер с RETRY (до 5 попыток с экспоненциальной задержкой)
            sms_data = get_phone_number_with_retry(max_retries=5)

            if sms_data:
                sms_activation_id = sms_data['activation_id']
                phone_number = sms_data['phone_number']

                # ОБРАБОТКА НОМЕРА: убрать код страны если нужно
                # Многие формы ожидают номер БЕЗ кода страны +1
                if phone_number.startswith('1') and len(phone_number) == 11:
                    phone_number_without_country = phone_number[1:]  # Убрать первую цифру "1"
                    print(f"[SMS] [INFO] Номер от API: {phone_number} (с кодом страны)")
                    print(f"[SMS] [INFO] Номер для формы: {phone_number_without_country} (без кода)")
                    data_row['phone_number'] = phone_number_without_country
                else:
                    # Номер в другом формате - используем как есть
                    print(f"[SMS] [INFO] Номер: {phone_number} (используем как есть)")
                    data_row['phone_number'] = phone_number

                print(f"[SMS] [OK] Activation ID: {sms_activation_id}")

                # ЗАПИСЬ В CSV: сохранить полученный номер для логирования
                update_csv_row(row_index=iteration_number - 1, phone_number=data_row['phone_number'])  # 🔥 Автовыбор режима
            else:
                # FAIL-FAST: НЕ ЗАПУСКАЕМ СКРИПТ БЕЗ НОМЕРА!
                print("[CRITICAL] ==========================================")
                print("[CRITICAL] НЕ УДАЛОСЬ ПОЛУЧИТЬ НОМЕР ОТ SMS API!")
                print("[CRITICAL] ПРЕРЫВАНИЕ ИТЕРАЦИИ - БЕЗ НОМЕРА НЕ ЗАПУСКАЕМ")
                print("[CRITICAL] ==========================================")
                return False  # Прервать итерацию
'''

        # OTP получение теперь встроено в пользовательский код (в парсере)
        # Парсер автоматически вставляет получение OTP перед заполнением OTP поля
        otp_helper = ''

        # ВСЕГДА используем Octobrowser (CDP режим)
        # Target влияет только на парсинг импортированного скрипта, но не на выполнение
        browser_launch_code = f'''
        # Проверить доступность Octobrowser Local API
        if not check_local_api():
            print("[ERROR] Octobrowser не запущен! Профили не смогут открыться.")
            print("[ERROR] Итерация прервана.")
            return False

        # Создать профиль
        profile_uuid = create_profile()
        if not profile_uuid:
            print("[ERROR] Не удалось создать профиль")
            return False

        # Запустить профиль
        debug_port = start_profile(profile_uuid)
        if not debug_port:
            print("[ERROR] Не удалось запустить профиль")
            return False

        # Подключиться к браузеру через CDP
        with sync_playwright() as p:
            cdp_url = f"http://127.0.0.1:{{debug_port}}"
            print(f"[CDP MODE] Подключение к Octobrowser через CDP: {{cdp_url}}")

            try:
                browser = p.chromium.connect_over_cdp(cdp_url)
                print("[OK] Playwright подключен к Octobrowser")
            except Exception as e:
                print(f"[ERROR] Не удалось подключиться к CDP: {{e}}")
                return False

            # Получить контекст и страницу
            if browser.contexts:
                context = browser.contexts[0]
                if context.pages:
                    page = context.pages[0]
                else:
                    page = context.new_page()
            else:
                print("[ERROR] Нет доступных контекстов браузера")
                return False

            print(f"[OK] Страница готова к автоматизации")
{otp_helper}
            # ============================================================
            # ПОЛЬЗОВАТЕЛЬСКИЙ КОД АВТОМАТИЗАЦИИ
            # ============================================================

{indented_code}

            # ============================================================

            print(f"[OK] Итерация #{{iteration_number}} успешно завершена")
            return True'''

        return f'''# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ ИТЕРАЦИИ
# ============================================================

def run_automation_iteration(iteration_number: int, data_row: Dict):
    """
    Запуск одной итерации автоматизации с Playwright

    Args:
        iteration_number: Номер итерации
        data_row: Данные из CSV для этой итерации
    """
    profile_uuid = None
    browser = None
    context = None
    page = None
    sms_activation_id = None  # 🔥 ВСЕГДА определяем, даже если SMS отключен

    print("\\n" + "="*60)
    print(f"Итерация #{{iteration_number}}")
    print(f"Данные: {{data_row}}")
    print("="*60 + "\\n")

    try:{sms_block}{browser_launch_code}

    except Exception as e:
        error_msg = str(e)
        if "target closed" in error_msg.lower() or "browser has been closed" in error_msg.lower():
            print(f"[!] ВНИМАНИЕ: Браузер был закрыт вручную!")
            print(f"Итерация #{{iteration_number}} прервана")
        elif "timeout" in error_msg.lower():
            print(f"[TIMEOUT] Элемент не найден в итерации #{{iteration_number}}")
            print(f"Возможно страница загружается слишком долго")
        else:
            print(f"[ERROR] Ошибка в итерации #{{iteration_number}}: {{e}}")

        import traceback
        traceback.print_exc()

        # Закрыть браузер и профиль ТОЛЬКО при ошибке
        print("[ERROR] Закрытие профиля из-за ошибки...")
        if browser:
            try:
                browser.close()
                print("[OK] Браузер закрыт")
            except:
                pass

        if profile_uuid:
            try:
                stop_profile(profile_uuid)
                print(f"[OK] Профиль {{profile_uuid}} остановлен")
            except:
                pass

        return False


'''

    def _generate_main_function(self) -> str:
        """Генерирует главную функцию"""
        return '''# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    """Главная функция с мультизапуском"""
    try:
        # Загрузить данные из CSV (встроенные или из файла)
        data_rows = load_data_from_csv()  # 🔥 Автоматически выберет режим

        if not data_rows:
            print("[ERROR] Нет данных для обработки!")
            return

        # Статистика
        total_iterations = len(data_rows)
        successful_iterations = 0
        failed_iterations = 0

        print(f"\\nЗапуск автоматизации для {total_iterations} строк данных\\n")

        # Запуск для каждой строки
        for i, data_row in enumerate(data_rows, start=1):
            success = run_automation_iteration(i, data_row)

            if success:
                successful_iterations += 1
            else:
                failed_iterations += 1

            # Пауза между итерациями
            if i < total_iterations:
                pause_seconds = 5
                print(f"\\nПауза {pause_seconds} секунд перед следующей итерацией...")
                time.sleep(pause_seconds)

        # Итоговая статистика
        print("\\n" + "="*60)
        print("ИТОГО:")
        print(f"Всего итераций: {total_iterations}")
        print(f"Успешных: {successful_iterations}")
        print(f"С ошибками: {failed_iterations}")
        print("="*60)

    except KeyboardInterrupt:
        print("\\n[ПРЕРВАНО] Выполнение остановлено пользователем")
    except Exception as e:
        print(f"\\n[ERROR] Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("="*60)
    print("Octobrowser Automation Script (Playwright SYNC)")
    print("="*60)
    main()
'''


def generate_playwright_script(user_code: str, config: Dict) -> str:
    """
    Вспомогательная функция для генерации Playwright скрипта

    Args:
        user_code: Код автоматизации
        config: Конфигурация

    Returns:
        Полный скрипт
    """
    generator = PlaywrightScriptGenerator()
    return generator.generate_script(user_code, config)
