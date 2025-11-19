"""
Network Parser - модуль для перехвата и парсинга Network данных из DevTools
Работает с Playwright для перехвата HTTP responses
"""

import json
import re
from typing import Dict, List, Optional, Callable
from playwright.sync_api import Page, Response


class NetworkParser:
    """Класс для перехвата и парсинга сетевых запросов"""

    def __init__(self):
        """Инициализация парсера"""
        self.captured_responses: List[Dict] = []
        self.response_filters: List[Dict] = []

    def add_filter(self, url_pattern: str, parser_func: Optional[Callable] = None):
        """
        Добавить фильтр для перехвата определенных URL

        Args:
            url_pattern: Regex паттерн для URL (например, ".*api/quote.*")
            parser_func: Функция для парсинга response (опционально)
        """
        self.response_filters.append({
            'pattern': url_pattern,
            'parser': parser_func
        })

    def attach_to_page(self, page: Page):
        """
        Подключить перехватчик к странице Playwright

        Args:
            page: Объект Page из Playwright
        """

        def handle_response(response: Response):
            """Обработчик для каждого response"""
            try:
                url = response.url
                status = response.status

                # Проверяем фильтры
                for filter_config in self.response_filters:
                    if re.search(filter_config['pattern'], url):
                        # Перехватываем response
                        self._capture_response(response, filter_config.get('parser'))

            except Exception as e:
                print(f"Ошибка при обработке response: {e}")

        # Подключаем обработчик к странице
        page.on("response", handle_response)

    def _capture_response(self, response: Response, parser_func: Optional[Callable] = None):
        """
        Захватить и сохранить response

        Args:
            response: Response объект из Playwright
            parser_func: Функция для кастомного парсинга
        """
        try:
            url = response.url
            status = response.status
            headers = response.headers

            # Пытаемся получить body
            body = None
            try:
                body = response.text()
            except Exception:
                # Response может быть бинарным или недоступным
                pass

            # Пытаемся распарсить JSON
            json_data = None
            if body:
                try:
                    json_data = json.loads(body)
                except json.JSONDecodeError:
                    pass

            captured_data = {
                'url': url,
                'status': status,
                'headers': headers,
                'body': body,
                'json': json_data
            }

            # Если есть кастомный парсер - используем его
            if parser_func:
                parsed_data = parser_func(captured_data)
                captured_data['parsed'] = parsed_data

            self.captured_responses.append(captured_data)

        except Exception as e:
            print(f"Ошибка захвата response: {e}")

    def get_all_responses(self) -> List[Dict]:
        """Получить все захваченные responses"""
        return self.captured_responses

    def find_responses_by_url(self, url_pattern: str) -> List[Dict]:
        """
        Найти responses по URL паттерну

        Args:
            url_pattern: Regex паттерн для поиска

        Returns:
            Список найденных responses
        """
        return [
            resp for resp in self.captured_responses
            if re.search(url_pattern, resp['url'])
        ]

    def extract_json_field(self, url_pattern: str, json_path: str) -> Optional[any]:
        """
        Извлечь поле из JSON response

        Args:
            url_pattern: Паттерн URL для поиска
            json_path: Путь к полю в JSON (разделенный точками, например "data.quote.id")

        Returns:
            Значение поля или None
        """
        responses = self.find_responses_by_url(url_pattern)

        for resp in responses:
            if resp.get('json'):
                value = self._get_nested_value(resp['json'], json_path)
                if value is not None:
                    return value

        return None

    def _get_nested_value(self, data: Dict, path: str) -> Optional[any]:
        """
        Получить вложенное значение из словаря по пути

        Args:
            data: Словарь с данными
            path: Путь к полю (например "data.quote.id")

        Returns:
            Значение или None
        """
        keys = path.split('.')
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

    def clear_responses(self):
        """Очистить список захваченных responses"""
        self.captured_responses = []

    def save_responses_to_file(self, filename: str):
        """
        Сохранить все захваченные responses в JSON файл

        Args:
            filename: Имя файла для сохранения
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.captured_responses, f, indent=2, ensure_ascii=False)
            print(f"Responses сохранены в {filename}")
        except Exception as e:
            print(f"Ошибка сохранения responses: {e}")


# Вспомогательные функции для популярных парсеров

def parse_quote_response(response_data: Dict) -> Dict:
    """
    Пример парсера для quote response

    Args:
        response_data: Данные response

    Returns:
        Распарсенные данные
    """
    result = {}

    if response_data.get('json'):
        json_data = response_data['json']

        # Примеры полей которые можно извлечь
        result['quote_id'] = json_data.get('quote_id') or json_data.get('id')
        result['premium'] = json_data.get('premium') or json_data.get('price')
        result['carrier'] = json_data.get('carrier_name') or json_data.get('carrier')

        # Можно добавить более сложную логику
        if 'data' in json_data:
            result['quote_id'] = json_data['data'].get('quote_id')
            result['premium'] = json_data['data'].get('premium_price')

    return result


def parse_policy_response(response_data: Dict) -> Dict:
    """
    Пример парсера для policy response

    Args:
        response_data: Данные response

    Returns:
        Распарсенные данные
    """
    result = {}

    if response_data.get('json'):
        json_data = response_data['json']

        result['policy_number'] = json_data.get('policy_number')
        result['policy_url'] = json_data.get('policy_url')
        result['effective_date'] = json_data.get('effective_date')

    return result
