"""
Provider: with_otp_placeholder
Генератор Playwright скриптов С OTP (placeholder для будущей реализации)
"""

import json
from typing import Dict, List


class Generator:
    """Генератор Playwright скриптов с OTP/SMS (TODO)"""

    def generate_script(self, user_code: str, config: Dict) -> str:
        """
        Генерирует полный Playwright скрипт с OTP

        Args:
            user_code: Пользовательский код автоматизации
            config: Конфигурация (API token, proxy, target, etc.)

        Returns:
            Полный исполняемый Python скрипт
        """
        api_token = config.get('api_token', '')
        use_proxy = config.get('use_proxy', False)
        proxy_config = config.get('proxy', {})
        csv_filename = config.get('csv_filename', 'data.csv')
        csv_data = config.get('csv_data', None)
        csv_embed_mode = config.get('csv_embed_mode', True)
        target = config.get('target', 'library')
        profile_config = config.get('profile', {})

        script = self._generate_imports()
        script += self._generate_config(api_token, proxy_config, use_proxy, csv_filename, csv_data, csv_embed_mode, target)
        # TODO: Add SMS/OTP configuration here
        script += self._generate_octobrowser_functions(profile_config)
        # TODO: Add SMS provider functions here
        script += self._generate_csv_loader()
        script += self._generate_main_iteration(user_code, target)
        script += self._generate_main_function()

        return script

    def _generate_imports(self) -> str:
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматически сгенерированный скрипт автоматизации
Фреймворк: Playwright (SYNC API)
Браузер: Octobrowser (через CDP)
Provider: with_otp_placeholder
"""

import csv
import time
import requests
from playwright.sync_api import sync_playwright, Playwright, expect
from typing import Dict, List, Optional

# TODO: Add SMS provider imports

'''

    def _generate_config(self, api_token: str, proxy_config: Dict, use_proxy: bool,
                         csv_filename: str, csv_data: List[Dict], csv_embed_mode: bool, target: str) -> str:
        config = f'''# ============================================================
# КОНФИГУРАЦИЯ
# ============================================================

# Playwright target
PLAYWRIGHT_TARGET = "{target}"

# Octobrowser API
API_BASE_URL = "https://app.octobrowser.net/api/v2/automation"
API_TOKEN = "{api_token}"
LOCAL_API_URL = "http://localhost:58888/api"

# TODO: OTP/SMS configuration here

'''

        if csv_embed_mode and csv_data:
            config += f'''# CSV данные (встроены в скрипт)
CSV_EMBED_MODE = True
CSV_DATA = {json.dumps(csv_data, ensure_ascii=False, indent=2)}

'''
        else:
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

        config += '\n\n'
        return config

    def _generate_octobrowser_functions(self, profile_config: Dict = None) -> str:
        if profile_config is None:
            profile_config = {}

        import json

        fingerprint = profile_config.get('fingerprint') or {"os": "win"}
        tags = profile_config.get('tags', [])
        notes = profile_config.get('notes', '')
        geolocation = profile_config.get('geolocation')

        fingerprint_json = json.dumps(fingerprint, ensure_ascii=False)
        tags_json = json.dumps(tags, ensure_ascii=False)
        geolocation_json = json.dumps(geolocation, ensure_ascii=False) if geolocation else 'None'

        return f'''# ============================================================
# ФУНКЦИИ OCTOBROWSER
# ============================================================

def create_profile(title: str = "Auto Profile") -> Optional[str]:
    """Создать профиль через API"""
    url = f"{{API_BASE_URL}}/profiles"
    headers = {{"X-Octo-Api-Token": API_TOKEN}}

    profile_data = {{
        "title": title,
        "fingerprint": {fingerprint_json},
        "tags": {tags_json},
        "notes": "{notes}"
    }}

    if {geolocation_json}:
        profile_data['geolocation'] = {geolocation_json}

    try:
        response = requests.post(url, headers=headers, json=profile_data)
        if response.status_code in [200, 201]:
            result = response.json()
            return result.get('data', {{}}).get('uuid')
    except Exception as e:
        print(f"[ERROR] Create profile: {{e}}")
    return None


def start_profile(profile_uuid: str) -> Optional[Dict]:
    """Запустить профиль и получить debug URL"""
    url = f"{{LOCAL_API_URL}}/profiles/{{profile_uuid}}/start"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"[ERROR] Start profile: {{e}}")
    return None


def stop_profile(profile_uuid: str):
    """Остановить профиль"""
    url = f"{{LOCAL_API_URL}}/profiles/{{profile_uuid}}/stop"
    try:
        requests.get(url)
    except:
        pass


def delete_profile(profile_uuid: str):
    """Удалить профиль"""
    url = f"{{API_BASE_URL}}/profiles/{{profile_uuid}}"
    headers = {{"X-Octo-Api-Token": API_TOKEN}}
    try:
        requests.delete(url, headers=headers)
    except:
        pass


# TODO: SMS provider functions here
# def get_phone_number() -> Optional[str]: ...
# def get_otp_code(phone: str) -> Optional[str]: ...

'''

    def _generate_csv_loader(self) -> str:
        return '''# ============================================================
# ЗАГРУЗКА CSV ДАННЫХ
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

    def _generate_main_iteration(self, user_code: str, target: str) -> str:
        return f'''# ============================================================
# ОСНОВНАЯ ФУНКЦИЯ ИТЕРАЦИИ
# ============================================================

def run_iteration(page, data_row: Dict, iteration_number: int):
    """
    Запуск одной итерации автоматизации

    Args:
        page: Playwright page object
        data_row: Строка данных из CSV
        iteration_number: Номер итерации (начиная с 1)
    """
    print(f"\\n[ITERATION {{iteration_number}}] Начало...")

    # TODO: OTP logic here (get phone, wait for SMS, fill OTP field)

    # ПОЛЬЗОВАТЕЛЬСКИЙ КОД
{self._indent_code(user_code, 4)}

    print(f"[ITERATION {{iteration_number}}] Завершено")


'''

    def _generate_main_function(self) -> str:
        return '''# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    """Главная функция запуска автоматизации"""
    print("[MAIN] Загрузка CSV данных...")
    csv_data = load_csv_data()
    print(f"[MAIN] Загружено {len(csv_data)} строк")

    if not csv_data:
        print("[ERROR] Нет данных для обработки")
        return

    for iteration_number, data_row in enumerate(csv_data, 1):
        print(f"\\n{'='*60}")
        print(f"[ROW {iteration_number}/{len(csv_data)}]")
        print(f"{'='*60}")

        profile_uuid = None

        try:
            # Создать профиль
            profile_title = f"Auto Profile {iteration_number}"
            print(f"[PROFILE] Создание профиля: {profile_title}")
            profile_uuid = create_profile(profile_title)

            if not profile_uuid:
                print("[ERROR] Не удалось создать профиль")
                continue

            print(f"[PROFILE] UUID: {profile_uuid}")

            # Запустить профиль
            print("[PROFILE] Запуск...")
            start_data = start_profile(profile_uuid)

            if not start_data:
                print("[ERROR] Не удалось запустить профиль")
                continue

            debug_url = start_data.get('ws_endpoint')
            if not debug_url:
                print("[ERROR] Нет debug URL")
                continue

            print(f"[PROFILE] Debug URL получен")

            # Подключиться через Playwright
            with sync_playwright() as playwright:
                browser = playwright.chromium.connect_over_cdp(debug_url)
                context = browser.contexts[0]
                page = context.pages[0]

                # Запуск итерации
                run_iteration(page, data_row, iteration_number)

                # Ждем перед закрытием
                time.sleep(2)

                browser.close()

            print(f"[PROFILE] Остановка профиля")
            stop_profile(profile_uuid)

        except Exception as e:
            print(f"[ERROR] Итерация {iteration_number}: {e}")
            import traceback
            traceback.print_exc()

        finally:
            if profile_uuid:
                time.sleep(1)

    print("\\n[MAIN] Все итерации завершены")


if __name__ == "__main__":
    main()
'''

    def _indent_code(self, code: str, spaces: int) -> str:
        indent = ' ' * spaces
        lines = code.split('\n')
        return '\n'.join(indent + line if line.strip() else '' for line in lines)
