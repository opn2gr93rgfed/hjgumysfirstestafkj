"""
Генератор Python скриптов для автоматизации с Octobrowser
"""
from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Добавляем путь к модулям проекта
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.template_engine import TemplateEngine


class ScriptGenerator:
    """Класс для генерации Python скриптов автоматизации"""

    def __init__(self):
        self.imports = set()
        self.code_blocks = []
        self.config = {}
        self.template_engine = TemplateEngine()

    def reset(self):
        """Сброс состояния генератора"""
        self.imports = set()
        self.code_blocks = []
        self.config = {}

    def set_config(self, config: Dict):
        """Установка конфигурации скрипта"""
        self.config = config

    def add_import(self, import_statement: str):
        """Добавление импорта"""
        self.imports.add(import_statement)

    def add_code_block(self, code: str, priority: int = 100):
        """
        Добавление блока кода

        Args:
            code: Код для добавления
            priority: Приоритет выполнения (меньше = раньше)
        """
        self.code_blocks.append((priority, code))

    def _generate_header(self) -> str:
        """Генерация заголовка скрипта"""
        header = f'''"""
Автоматически сгенерированный скрипт автоматизации
Создан: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Генератор: Octobrowser Script Builder
"""

'''
        return header

    def _generate_imports(self) -> str:
        """Генерация секции импортов"""
        if not self.imports:
            return ""

        imports_code = "\n".join(sorted(self.imports))
        return f"{imports_code}\n\n"

    def _generate_config_section(self) -> str:
        """Генерация секции конфигурации"""
        if not self.config:
            return ""

        config_code = "# Конфигурация\n"
        config_code += f"API_TOKEN = '{self.config.get('api_token', 'YOUR_API_TOKEN')}'\n"
        config_code += f"API_BASE_URL = '{self.config.get('api_base_url', 'https://app.octobrowser.net/api/v2/automation')}'\n"
        config_code += f"LOCAL_API_BASE_URL = 'http://localhost:58888/api/v1'  # Локальный API для запуска профилей\n\n"

        return config_code

    def _generate_profile_creation(self, profile_config: Dict) -> str:
        """Генерация кода создания профиля"""
        code = '''
def create_profile():
    """Создание профиля в Octobrowser"""
    import requests

    headers = {
        'X-Octo-Api-Token': API_TOKEN,
        'Content-Type': 'application/json'
    }

    profile_data = {
'''

        # Добавляем настройки профиля
        if profile_config.get('title'):
            code += f"        'title': '{profile_config['title']}',\n"

        # Fingerprint - ОБЯЗАТЕЛЬНОЕ ПОЛЕ
        # Если не указан, создаем дефолтный
        if profile_config.get('fingerprint'):
            fp = profile_config['fingerprint']
            # Исправляем структуру: os_type -> os
            os_value = fp.get('os_type', 'win')
            code += f"        'fingerprint': {{'os': '{os_value}'}},\n"
        else:
            # Дефолтный fingerprint если не указан
            code += f"        'fingerprint': {{'os': 'win'}},\n"

        if profile_config.get('tags'):
            code += f"        'tags': {profile_config['tags']},\n"

        # Proxy - важно для работы с антидетект-браузером
        if profile_config.get('proxy'):
            proxy = profile_config['proxy']
            # Убедимся что port - число
            port = proxy.get('port', 0)
            if isinstance(port, str):
                try:
                    port = int(port)
                except ValueError:
                    port = 0

            code += f'''        'proxy': {{
            'type': '{proxy.get('type', 'http')}',
            'host': '{proxy.get('host', '')}',
            'port': {port},
            'login': '{proxy.get('login', '')}',
            'password': '{proxy.get('password', '')}'
        }},\n'''

        code += '''    }

    # Отладочный вывод отправляемых данных
    print(f"DEBUG: Создание профиля с данными:")
    print(f"  - Title: {profile_data.get('title', 'N/A')}")
    if 'proxy' in profile_data:
        print(f"  - Proxy type: {profile_data['proxy'].get('type', 'N/A')}")
        print(f"  - Proxy host: {profile_data['proxy'].get('host', 'N/A')}")
        print(f"  - Proxy port: {profile_data['proxy'].get('port', 'N/A')}")
        print(f"  - Proxy login: {profile_data['proxy'].get('login', 'N/A')}")
    else:
        print(f"  - Proxy: НЕ УКАЗАН")

    response = requests.post(
        f"{API_BASE_URL}/profiles",
        headers=headers,
        json=profile_data
    )

    print(f"DEBUG: HTTP Status Code = {response.status_code}")
    print(f"DEBUG: Response Text = {response.text}")

    if response.status_code in [200, 201]:
        result = response.json()

        # === ОТЛАДКА ===
        print(f"DEBUG: type(result) = {type(result)}")
        print(f"DEBUG: result.keys() = {result.keys() if isinstance(result, dict) else 'NOT A DICT'}")
        print(f"DEBUG: 'data' in result = {'data' in result if isinstance(result, dict) else False}")
        print(f"DEBUG: result.get('data') = {result.get('data') if isinstance(result, dict) else None}")
        print(f"DEBUG: Full result = {result}")

        # API возвращает структуру: {"success": true, "data": {"uuid": "..."}}
        if isinstance(result, dict) and 'data' in result and result['data'] and 'uuid' in result['data']:
            uuid = result['data']['uuid']
            print(f"Профиль создан: {uuid}")
            return uuid
        else:
            print(f"Ошибка создания профиля: {response.text}")
            return None
    else:
        print(f"Ошибка создания профиля: {response.text}")
        return None

'''
        return code

    def _generate_profile_check(self) -> str:
        """Генерация кода проверки существования профиля"""
        code = '''
def check_profile_exists(profile_uuid):
    """Проверка существования профиля"""
    import requests

    headers = {
        'X-Octo-Api-Token': API_TOKEN,
        'Content-Type': 'application/json'
    }

    url = f"{API_BASE_URL}/profiles/{profile_uuid}"
    print(f"DEBUG CHECK: Проверка профиля по URL = {url}")

    response = requests.get(url, headers=headers)

    print(f"DEBUG CHECK: HTTP Status Code = {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        if 'data' in result and result['data']:
            profile_data = result['data']
            print(f"[OK] Профиль найден: {profile_data.get('title', 'Без названия')}")

            # Проверка прокси
            if 'proxy' in profile_data and profile_data['proxy']:
                proxy = profile_data['proxy']
                print(f"[PROXY] Прокси установлен:")
                print(f"  - Тип: {proxy.get('type', 'N/A')}")
                print(f"  - Хост: {proxy.get('host', 'N/A')}")
                print(f"  - Порт: {proxy.get('port', 'N/A')}")
                print(f"  - Логин: {proxy.get('login', 'N/A')}")
            else:
                print(f"[PROXY] Прокси НЕ установлен (используется прямое подключение)")

            return True
        else:
            print(f"[ОШИБКА] Профиль не найден в ответе: {response.text}")
            return False
    else:
        print(f"[ОШИБКА] Ошибка проверки профиля: {response.text}")
        return False

'''
        return code

    def _generate_profile_start(self) -> str:
        """Генерация кода запуска профиля"""
        code = '''
def start_profile(profile_uuid):
    """Запуск профиля через локальный API Octobrowser"""
    import requests
    import time

    # Небольшая задержка после создания профиля
    print(f"Ожидание инициализации профиля {profile_uuid}...")
    time.sleep(2)

    # Правильный endpoint для локального API (из официальной документации)
    url = "http://localhost:58888/api/profiles/start"

    # Параметры запуска
    payload = {
        "uuid": profile_uuid,
        "headless": False,  # Показывать интерфейс браузера
        "debug_port": True  # Включить debug port для Selenium
    }

    print(f"Запуск профиля через локальный API...")
    print(f"URL: {url}")
    print(f"Payload: {payload}")

    try:
        response = requests.post(url, json=payload, timeout=10)

        print(f"Status: {response.status_code}")

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"Response: {result}")

            # Ищем debug_port в ответе
            debug_port = None
            if isinstance(result, dict):
                # Пробуем разные варианты структуры ответа
                if 'data' in result and isinstance(result['data'], dict):
                    debug_port = result['data'].get('debug_port') or result['data'].get('port') or result['data'].get('ws_endpoint')
                elif 'debug_port' in result:
                    debug_port = result['debug_port']
                elif 'port' in result:
                    debug_port = result['port']
                elif 'ws_endpoint' in result:
                    # Если возвращается WebSocket endpoint, извлекаем порт
                    ws = result['ws_endpoint']
                    if ':' in str(ws):
                        debug_port = str(ws).split(':')[-1].split('/')[0]

            if debug_port:
                print(f"[OK] Профиль запущен на порту: {debug_port}")
                return debug_port
            else:
                print(f"[ПРЕДУПРЕЖДЕНИЕ] Профиль запущен, но debug_port не найден в ответе")
                print(f"Попробуйте использовать стандартный порт 9222")
                return 9222

        else:
            print(f"[ОШИБКА] HTTP {response.status_code}: {response.text}")

    except requests.exceptions.ConnectionError:
        print(f"[ОШИБКА] Не удалось подключиться к локальному API Octobrowser")
        print(f"[РЕШЕНИЕ] Убедитесь, что приложение Octobrowser ЗАПУЩЕНО")
    except Exception as e:
        print(f"[ОШИБКА] {e}")

    return None

'''
        return code

    def _generate_selenium_connection(self) -> str:
        """Генерация кода подключения Selenium"""
        code = '''
def connect_selenium(debug_port):
    """Подключение Selenium к профилю с повторными попытками"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import time

    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")

    # Ждем инициализации браузера
    print(f"Ожидание инициализации Chrome DevTools на порту {debug_port}...")
    time.sleep(5)  # Даем браузеру время на полную инициализацию

    # Пытаемся подключиться с повторными попытками
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Попытка подключения Selenium {attempt}/{max_attempts}...")
            driver = webdriver.Chrome(options=options)
            print("[OK] Selenium успешно подключен к профилю")
            return driver
        except Exception as e:
            if attempt < max_attempts:
                wait_time = attempt * 2  # Экспоненциальная задержка: 2, 4, 6, 8 секунд
                print(f"[ПРЕДУПРЕЖДЕНИЕ] Не удалось подключиться: {e}")
                print(f"Повторная попытка через {wait_time} секунд...")
                time.sleep(wait_time)
            else:
                print(f"[ОШИБКА] Не удалось подключить Selenium после {max_attempts} попыток")
                raise

'''
        return code

    def _generate_profile_stop(self) -> str:
        """Генерация кода остановки профиля"""
        code = '''
def stop_profile(profile_uuid):
    """Остановка профиля через локальный API"""
    import requests

    # Правильный endpoint для остановки (из официальной документации)
    url = "http://localhost:58888/api/profiles/stop"

    payload = {
        "uuid": profile_uuid
    }

    print(f"Остановка профиля {profile_uuid}...")

    try:
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code in [200, 201]:
            print("[OK] Профиль остановлен")
            return True
        else:
            print(f"[ОШИБКА] HTTP {response.status_code}: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[ОШИБКА] Octobrowser не запущен или недоступен")
        return False
    except Exception as e:
        print(f"[ОШИБКА] {e}")
        return False

'''
        return code

    def _generate_cookies_management(self, cookies_data: List[Dict]) -> str:
        """Генерация кода управления cookies"""
        code = '''
def add_cookies(profile_uuid, cookies):
    """Добавление cookies в профиль"""
    import requests

    headers = {
        'X-Octo-Api-Token': API_TOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.post(
        f"{API_BASE_URL}/profiles/{profile_uuid}/cookies",
        headers=headers,
        json={'cookies': cookies}
    )

    if response.status_code in [200, 201]:
        print(f"Добавлено {len(cookies)} cookies")
        return True
    else:
        print(f"Ошибка добавления cookies: {response.text}")
        return False

'''
        if cookies_data:
            code += f"\n# Предустановленные cookies\nPREDEFINED_COOKIES = {cookies_data}\n\n"

        return code

    def _generate_bookmarks_management(self, bookmarks_data: List[Dict]) -> str:
        """Генерация кода управления закладками"""
        code = '''
def add_bookmarks(profile_uuid, bookmarks):
    """Добавление закладок в профиль"""
    import requests

    headers = {
        'X-Octo-Api-Token': API_TOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.post(
        f"{API_BASE_URL}/profiles/{profile_uuid}/bookmarks",
        headers=headers,
        json={'bookmarks': bookmarks}
    )

    if response.status_code in [200, 201]:
        print(f"Добавлено {len(bookmarks)} закладок")
        return True
    else:
        print(f"Ошибка добавления закладок: {response.text}")
        return False

'''
        if bookmarks_data:
            code += f"\n# Предустановленные закладки\nPREDEFINED_BOOKMARKS = {bookmarks_data}\n\n"

        return code

    def _generate_extensions_management(self, extensions_data: List[str]) -> str:
        """Генерация кода управления расширениями"""
        code = '''
def add_extension(profile_uuid, extension_path):
    """Добавление расширения в профиль"""
    import requests

    headers = {
        'X-Octo-Api-Token': API_TOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.post(
        f"{API_BASE_URL}/profiles/{profile_uuid}/extensions",
        headers=headers,
        json={'path': extension_path}
    )

    if response.status_code in [200, 201]:
        print(f"Расширение добавлено: {extension_path}")
        return True
    else:
        print(f"Ошибка добавления расширения: {response.text}")
        return False

'''
        if extensions_data:
            code += f"\n# Предустановленные расширения\nPREDEFINED_EXTENSIONS = {extensions_data}\n\n"

        return code

    def _generate_main_function(self, user_code: str, use_profile_creation: bool,
                                use_selenium: bool, cleanup_profile: bool,
                                use_cookies: bool = False, use_bookmarks: bool = False,
                                use_extensions: bool = False) -> str:
        """Генерация главной функции"""
        code = '''
def main():
    """Главная функция автоматизации"""
    profile_uuid = None
    driver = None

    try:
'''

        # Создание профиля
        if use_profile_creation:
            code += '''        # Создание профиля
        profile_uuid = create_profile()
        if not profile_uuid:
            print("Не удалось создать профиль")
            return

'''

        # Добавление cookies
        if use_cookies:
            code += '''        # Добавление cookies
        if 'PREDEFINED_COOKIES' in globals() and PREDEFINED_COOKIES:
            add_cookies(profile_uuid, PREDEFINED_COOKIES)

'''

        # Добавление bookmarks
        if use_bookmarks:
            code += '''        # Добавление закладок
        if 'PREDEFINED_BOOKMARKS' in globals() and PREDEFINED_BOOKMARKS:
            add_bookmarks(profile_uuid, PREDEFINED_BOOKMARKS)

'''

        # Добавление extensions
        if use_extensions:
            code += '''        # Добавление расширений
        if 'PREDEFINED_EXTENSIONS' in globals() and PREDEFINED_EXTENSIONS:
            for ext_path in PREDEFINED_EXTENSIONS:
                add_extension(profile_uuid, ext_path)

'''

        # Запуск профиля
        if use_profile_creation:
            code += '''        # Проверка существования профиля
        if not check_profile_exists(profile_uuid):
            print("Профиль не найден в системе")
            return

        # Запуск профиля
        debug_port = start_profile(profile_uuid)
        if not debug_port:
            print("Не удалось запустить профиль")
            return

'''

        # Подключение Selenium (только если профиль создается)
        if use_selenium and use_profile_creation:
            code += '''        # Подключение Selenium
        driver = connect_selenium(debug_port)

'''
        elif use_selenium and not use_profile_creation:
            # Если Selenium включен, но профиль не создается - предупреждение
            code += '''        # ВНИМАНИЕ: Selenium требует создания профиля!
        # Включите "Создать новый профиль" для использования Selenium
        print("ОШИБКА: Невозможно подключить Selenium без создания профиля")
        return

'''

        # Пользовательский код
        if user_code.strip():
            code += f'''        # Пользовательский код автоматизации
{self._indent_code(user_code, 2)}

'''

        # Cleanup
        code += '''    except Exception as e:
        print(f"Ошибка выполнения: {e}")
        import traceback
        traceback.print_exc()

    finally:
'''

        if use_selenium:
            code += '''        # Закрытие браузера
        if driver:
            driver.quit()

'''

        if cleanup_profile:
            code += '''        # Остановка и удаление профиля
        if profile_uuid:
            stop_profile(profile_uuid)
            # Можно добавить удаление профиля если нужно

'''

        code += '''
if __name__ == "__main__":
    main()
'''

        return code

    def _indent_code(self, code: str, indent_level: int) -> str:
        """Добавление отступов к коду"""
        indent = "    " * indent_level
        lines = code.split('\n')
        return '\n'.join([indent + line if line.strip() else line for line in lines])

    def _generate_data_loader(self, data_file_path: str) -> str:
        """Генерация кода загрузки данных из CSV"""
        # Получаем только имя файла (без пути)
        import os
        csv_filename = os.path.basename(data_file_path)

        code = f'''
def find_csv_file(csv_filename):
    """Поиск CSV файла в нескольких возможных местах"""
    import os

    # Список мест для поиска файла
    search_paths = [
        csv_filename,  # Текущая директория
        os.path.join(os.path.dirname(__file__), csv_filename),  # Директория скрипта
        os.path.join(os.path.dirname(__file__), '..', csv_filename),  # Родительская директория
        r"{data_file_path}",  # Исходный абсолютный путь
    ]

    for path in search_paths:
        if os.path.exists(path):
            print(f"[OK] CSV файл найден: {{os.path.abspath(path)}}")
            return path

    # Если файл не найден, показываем подробную ошибку
    print(f"[ОШИБКА] CSV файл '{{csv_filename}}' не найден!")
    print(f"Искали в следующих местах:")
    for path in search_paths:
        print(f"  - {{os.path.abspath(path)}}")
    raise FileNotFoundError(f"CSV файл '{{csv_filename}}' не найден. Проверьте путь и поместите файл в одну из указанных директорий.")

def load_data_from_csv(csv_filename):
    """Загрузка данных из CSV файла"""
    import csv

    # Находим CSV файл
    csv_path = find_csv_file(csv_filename)

    data_rows = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        data_rows = list(reader)

    print(f"Загружено {{len(data_rows)}} строк данных из CSV")
    return data_rows

# Имя файла с данными
CSV_FILENAME = r"{csv_filename}"
'''
        return code

    def _generate_parametrized_main_function(self, user_code: str, use_profile_creation: bool,
                                            use_selenium: bool, cleanup_profile: bool,
                                            use_cookies: bool = False, use_bookmarks: bool = False,
                                            use_extensions: bool = False,
                                            data_file_path: Optional[str] = None) -> str:
        """Генерация главной функции с параметризацией"""

        code = '''
def run_automation_iteration(iteration_number, data_row):
    """
    Запуск одной итерации автоматизации с конкретными данными

    Args:
        iteration_number: Номер итерации (начиная с 1)
        data_row: Словарь с данными для этой итерации
    """
    profile_uuid = None
    driver = None

    print(f"\\n{'='*60}")
    print(f"Итерация #{iteration_number}")
    print(f"Данные: {data_row}")
    print(f"{'='*60}\\n")

    try:
'''

        # Создание профиля
        if use_profile_creation:
            code += '''        # Создание профиля
        profile_uuid = create_profile()
        if not profile_uuid:
            print("Не удалось создать профиль")
            return False

'''

        # Добавление cookies
        if use_cookies:
            code += '''        # Добавление cookies
        if 'PREDEFINED_COOKIES' in globals() and PREDEFINED_COOKIES:
            add_cookies(profile_uuid, PREDEFINED_COOKIES)

'''

        # Добавление bookmarks
        if use_bookmarks:
            code += '''        # Добавление закладок
        if 'PREDEFINED_BOOKMARKS' in globals() and PREDEFINED_BOOKMARKS:
            add_bookmarks(profile_uuid, PREDEFINED_BOOKMARKS)

'''

        # Добавление extensions
        if use_extensions:
            code += '''        # Добавление расширений
        if 'PREDEFINED_EXTENSIONS' in globals() and PREDEFINED_EXTENSIONS:
            for ext_path in PREDEFINED_EXTENSIONS:
                add_extension(profile_uuid, ext_path)

'''

        # Запуск профиля
        if use_profile_creation:
            code += '''        # Проверка существования профиля
        if not check_profile_exists(profile_uuid):
            print("Профиль не найден в системе")
            return False

        # Запуск профиля
        debug_port = start_profile(profile_uuid)
        if not debug_port:
            print("Не удалось запустить профиль")
            return False

'''

        # Подключение Selenium (только если профиль создается)
        if use_selenium and use_profile_creation:
            code += '''        # Подключение Selenium
        driver = connect_selenium(debug_port)

'''
        elif use_selenium and not use_profile_creation:
            # Если Selenium включен, но профиль не создается - предупреждение
            code += '''        # ВНИМАНИЕ: Selenium требует создания профиля!
        print("ОШИБКА: Невозможно подключить Selenium без создания профиля")
        return False

'''

        # Пользовательский код с заменой переменных
        if user_code.strip():
            # Находим все переменные в коде пользователя
            variables = self.template_engine.find_variables(user_code)

            if variables:
                code += '''        # Подготовка переменных из данных
'''
                for var in variables:
                    code += f'''        {var} = data_row.get('{var}', '')
'''
                code += '\n'

            # Заменяем {{variable}} на просто variable (переменную Python)
            user_code_processed = user_code
            for var in variables:
                user_code_processed = user_code_processed.replace(f'{{{{{var}}}}}', var)

            code += f'''        # Пользовательский код автоматизации
{self._indent_code(user_code_processed, 2)}

'''

        code += '''        print(f"Итерация #{iteration_number} успешно завершена")
        return True

    except Exception as e:
        error_msg = str(e)
        if "invalid session id" in error_msg.lower() or "session deleted" in error_msg.lower():
            print(f"⚠️ ВНИМАНИЕ: Браузер был закрыт вручную или потерял соединение!")
            print(f"Итерация #{iteration_number} прервана из-за закрытия браузера")
        elif "timeout" in error_msg.lower():
            print(f"⏱️ TIMEOUT: Элемент не найден за 30 секунд в итерации #{iteration_number}")
            print(f"Возможно страница загружается слишком долго или селектор неверный")
        else:
            print(f"Ошибка в итерации #{iteration_number}: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
'''

        if use_selenium:
            code += '''        # Закрытие браузера
        if driver:
            try:
                driver.quit()
            except:
                pass

'''

        if cleanup_profile:
            code += '''        # Остановка профиля
        if profile_uuid:
            try:
                stop_profile(profile_uuid)
            except:
                pass

'''

        code += '''

def main():
    """Главная функция с мультизапуском"""
    try:
        # Загрузка данных
        data_rows = load_data_from_csv(CSV_FILENAME)

        if not data_rows:
            print("Нет данных для обработки!")
            return

        # Статистика
        total_iterations = len(data_rows)
        successful_iterations = 0
        failed_iterations = 0

        print(f"Запуск автоматизации для {total_iterations} строк данных\\n")

        # Запуск для каждой строки данных
        for i, data_row in enumerate(data_rows, start=1):
            success = run_automation_iteration(i, data_row)

            if success:
                successful_iterations += 1
            else:
                failed_iterations += 1

            # Пауза между итерациями (чтобы система успела закрыть предыдущий профиль)
            if i < total_iterations:
                pause_seconds = 5
                print(f"\\nПауза {pause_seconds} секунд перед следующей итерацией...")
                time.sleep(pause_seconds)

        # Итоговая статистика
        print(f"\\n{'='*60}")
        print(f"ИТОГО:")
        print(f"Всего итераций: {total_iterations}")
        print(f"Успешных: {successful_iterations}")
        print(f"С ошибками: {failed_iterations}")
        print(f"{'='*60}")

    except FileNotFoundError as e:
        print(f"[ОШИБКА] CSV файл не найден!")
        print(f"Детали: {e}")
        print("\\nПоместите CSV файл в одну из следующих директорий:")
        print(f"  - В директорию со скриптом")
        print(f"  - В родительскую директорию")
        print(f"  - Укажите полный путь в настройках приложения")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
'''

        return code

    def generate_script(self, options: Dict, user_code: str = "") -> str:
        """
        Генерация полного скрипта

        Args:
            options: Опции генерации
            user_code: Пользовательский код автоматизации

        Returns:
            Полный код скрипта
        """
        self.reset()

        # Устанавливаем конфигурацию из options
        self.set_config(options)

        # Базовые импорты
        self.add_import("import time")
        self.add_import("import random")
        self.add_import("import sys")

        # Selenium импорты (если используется Selenium)
        if options.get('use_selenium', False):
            self.add_import("from selenium.webdriver.common.by import By")
            self.add_import("from selenium.webdriver.support.ui import WebDriverWait")
            self.add_import("from selenium.webdriver.support import expected_conditions as EC")
            self.add_import("from selenium.common.exceptions import TimeoutException, NoSuchElementException")

        script = self._generate_header()
        script += self._generate_imports()
        script += self._generate_config_section()

        # Если включена параметризация - добавляем загрузчик данных
        if options.get('use_parametrization', False) and options.get('data_file_path'):
            script += self._generate_data_loader(options.get('data_file_path'))

        # Добавляем функции в зависимости от опций
        if options.get('create_profile', False):
            script += self._generate_profile_creation(options.get('profile_config', {}))
            script += self._generate_profile_check()
            script += self._generate_profile_start()
            script += self._generate_profile_stop()

        # Cookies
        if options.get('use_cookies', False):
            script += self._generate_cookies_management(options.get('cookies_data', []))

        # Bookmarks
        if options.get('use_bookmarks', False):
            script += self._generate_bookmarks_management(options.get('bookmarks_data', []))

        # Extensions
        if options.get('use_extensions', False):
            script += self._generate_extensions_management(options.get('extensions_data', []))

        if options.get('use_selenium', False):
            script += self._generate_selenium_connection()

        # Главная функция: параметризованная или обычная
        if options.get('use_parametrization', False):
            script += self._generate_parametrized_main_function(
                user_code,
                options.get('create_profile', False),
                options.get('use_selenium', False),
                options.get('cleanup_profile', False),
                options.get('use_cookies', False),
                options.get('use_bookmarks', False),
                options.get('use_extensions', False),
                options.get('data_file_path')
            )
        else:
            script += self._generate_main_function(
                user_code,
                options.get('create_profile', False),
                options.get('use_selenium', False),
                options.get('cleanup_profile', False),
                options.get('use_cookies', False),
                options.get('use_bookmarks', False),
                options.get('use_extensions', False)
            )

        return script
