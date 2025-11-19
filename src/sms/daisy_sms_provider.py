"""
Реализация провайдера DaisySMS
"""
import requests
import time
from typing import Dict, Optional
from .base_provider import BaseSMSProvider, SMSStatus


class DaisySMSProvider(BaseSMSProvider):
    """
    Провайдер для работы с DaisySMS API

    Документация: https://daisysms.com/docs/api
    """

    BASE_URL = "https://daisysms.com/stubs/handler_api.php"

    def __init__(self, api_key: str, **kwargs):
        """
        Инициализация DaisySMS провайдера

        Args:
            api_key: API ключ DaisySMS
            **kwargs: Дополнительные параметры
        """
        super().__init__(api_key, **kwargs)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'auto2tesst/1.0'
        })

    def _make_request(self, action: str, **params) -> str:
        """
        Выполнить API запрос

        Args:
            action: Действие API
            **params: Дополнительные параметры

        Returns:
            Текстовый ответ от API
        """
        params['api_key'] = self.api_key
        params['action'] = action

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.text.strip()
        except requests.RequestException as e:
            return f"ERROR:{str(e)}"

    def get_balance(self) -> Dict:
        """
        Получить баланс

        Returns:
            Dict: {'balance': float, 'currency': 'USD', 'success': bool, 'error': Optional[str]}
        """
        response = self._make_request('getBalance')

        if response.startswith('ACCESS_BALANCE:'):
            balance = float(response.split(':')[1])
            return {
                'balance': balance,
                'currency': 'USD',
                'success': True,
                'error': None
            }
        else:
            return {
                'balance': 0.0,
                'currency': 'USD',
                'success': False,
                'error': response
            }

    def get_services(self) -> Dict:
        """
        Получить список сервисов и цен

        Returns:
            Dict: {'services': List[Dict], 'success': bool, 'error': Optional[str]}
        """
        response = self._make_request('getPrices')

        # Парсинг ответа getPrices (формат зависит от API)
        # Временная заглушка - возвращаем популярные сервисы
        if not response.startswith('ERROR'):
            services = [
                {'code': 'ds', 'name': 'Discord', 'price': 0.5},
                {'code': 'go', 'name': 'Google', 'price': 0.3},
                {'code': 'wa', 'name': 'WhatsApp', 'price': 0.8},
                {'code': 'tg', 'name': 'Telegram', 'price': 0.4},
                {'code': 'fb', 'name': 'Facebook', 'price': 0.6},
                {'code': 'ig', 'name': 'Instagram', 'price': 0.7},
                {'code': 'tw', 'name': 'Twitter', 'price': 0.9},
                {'code': 'vk', 'name': 'VKontakte', 'price': 0.2},
                {'code': 'ok', 'name': 'Odnoklassniki', 'price': 0.2},
                {'code': 'other', 'name': 'Other', 'price': 1.0}
            ]
            return {
                'services': services,
                'success': True,
                'error': None
            }
        else:
            return {
                'services': [],
                'success': False,
                'error': response
            }

    def get_number(self, service: str, **params) -> Dict:
        """
        Арендовать номер

        Args:
            service: Код сервиса (например, 'ds' для Discord)
            **params: Дополнительные параметры:
                - max_price: Максимальная цена
                - areas: Коды областей
                - carriers: Оператор (tmo, vz, att)
                - number: Конкретный номер

        Returns:
            Dict: {
                'activation_id': str,
                'phone_number': str,
                'service': str,
                'success': bool,
                'error': Optional[str]
            }
        """
        # Формирование параметров запроса
        request_params = {'service': service}

        if 'max_price' in params:
            request_params['max_price'] = params['max_price']
        if 'areas' in params:
            request_params['areas'] = params['areas']
        if 'carriers' in params:
            request_params['carriers'] = params['carriers']
        if 'number' in params:
            request_params['number'] = params['number']

        response = self._make_request('getNumber', **request_params)

        # Формат ответа: ACCESS_NUMBER:ID:PHONE_NUMBER
        if response.startswith('ACCESS_NUMBER:'):
            parts = response.split(':')
            activation_id = parts[1]
            phone_number = parts[2]

            # Сохраняем активацию
            self._add_activation(activation_id, {
                'phone_number': phone_number,
                'service': service,
                'timestamp': time.time()
            })

            return {
                'activation_id': activation_id,
                'phone_number': phone_number,
                'service': service,
                'success': True,
                'error': None
            }
        else:
            return {
                'activation_id': None,
                'phone_number': None,
                'service': service,
                'success': False,
                'error': response
            }

    def get_sms_code(self, activation_id: str, timeout: int = 180) -> Dict:
        """
        Получить SMS код

        Args:
            activation_id: ID активации
            timeout: Максимальное время ожидания (секунды)

        Returns:
            Dict: {
                'code': str,
                'full_text': str,
                'status': SMSStatus,
                'success': bool,
                'error': Optional[str]
            }
        """
        start_time = time.time()
        poll_interval = 3  # Минимум 3 секунды между запросами (по документации)

        while (time.time() - start_time) < timeout:
            response = self._make_request('getStatus', id=activation_id)

            # STATUS_OK:CODE - SMS получено
            if response.startswith('STATUS_OK:'):
                code = response.split(':')[1]
                self._remove_activation(activation_id)

                return {
                    'code': code,
                    'full_text': response,
                    'status': SMSStatus.RECEIVED,
                    'success': True,
                    'error': None
                }

            # STATUS_WAIT_CODE - ожидание
            elif response == 'STATUS_WAIT_CODE':
                time.sleep(poll_interval)
                continue

            # STATUS_CANCEL - отменено
            elif response == 'STATUS_CANCEL':
                self._remove_activation(activation_id)
                return {
                    'code': None,
                    'full_text': response,
                    'status': SMSStatus.CANCELLED,
                    'success': False,
                    'error': 'Активация отменена'
                }

            # NO_ACTIVATION - неверный ID
            elif response == 'NO_ACTIVATION':
                self._remove_activation(activation_id)
                return {
                    'code': None,
                    'full_text': response,
                    'status': SMSStatus.ERROR,
                    'success': False,
                    'error': 'Активация не найдена'
                }

            # Другие ошибки
            else:
                time.sleep(poll_interval)

        # Timeout
        return {
            'code': None,
            'full_text': None,
            'status': SMSStatus.TIMEOUT,
            'success': False,
            'error': f'Превышено время ожидания ({timeout}s)'
        }

    def cancel_activation(self, activation_id: str) -> Dict:
        """
        Отменить активацию

        Args:
            activation_id: ID активации

        Returns:
            Dict: {'success': bool, 'error': Optional[str]}
        """
        response = self._make_request('setStatus', id=activation_id, status=8)

        if response == 'ACCESS_CANCEL':
            self._remove_activation(activation_id)
            return {
                'success': True,
                'error': None
            }
        else:
            return {
                'success': False,
                'error': response
            }

    def finish_activation(self, activation_id: str) -> Dict:
        """
        Завершить активацию

        Args:
            activation_id: ID активации

        Returns:
            Dict: {'success': bool, 'error': Optional[str]}
        """
        response = self._make_request('setStatus', id=activation_id, status=6)

        if response == 'ACCESS_ACTIVATION':
            self._remove_activation(activation_id)
            return {
                'success': True,
                'error': None
            }
        else:
            return {
                'success': False,
                'error': response
            }

    def get_extra_activation(self, activation_id: str) -> Dict:
        """
        Запросить дополнительный код для той же активации

        Args:
            activation_id: ID активации

        Returns:
            Dict: {'success': bool, 'error': Optional[str]}
        """
        response = self._make_request('getExtraActivation', id=activation_id)

        if response == 'ACCESS_ACTIVATION':
            return {
                'success': True,
                'error': None
            }
        else:
            return {
                'success': False,
                'error': response
            }

    def get_all_services_with_prices(self) -> Dict:
        """
        Получить полный список всех доступных сервисов с ценами

        API endpoint: getPricesVerification
        Возвращает: service => country => data

        Returns:
            Dict: {
                'success': bool,
                'services': List[Dict],  # [{'code': 'ds', 'name': 'Discord', 'price': 0.5, 'country': 'USA'}, ...]
                'raw_data': Dict,  # Исходные данные от API
                'error': Optional[str]
            }
        """
        try:
            response = self._make_request('getPricesVerification')

            # Попробуем распарсить JSON
            import json
            try:
                data = json.loads(response)
            except (json.JSONDecodeError, ValueError):
                # Если не JSON, вернем ошибку
                return {
                    'success': False,
                    'services': [],
                    'raw_data': {},
                    'error': f'Invalid response format: {response[:100]}'
                }

            # Парсим структуру service => country => data
            services_list = []

            for service_code, countries_data in data.items():
                if isinstance(countries_data, dict):
                    for country_code, service_info in countries_data.items():
                        if isinstance(service_info, dict):
                            # Извлекаем данные о сервисе
                            service_entry = {
                                'code': service_code,
                                'country': country_code,
                                'name': service_info.get('name', service_code.upper()),
                                'price': float(service_info.get('price', 0)),
                                'count': service_info.get('count', 0)  # Количество доступных номеров
                            }
                            services_list.append(service_entry)

            # Сортируем по имени
            services_list.sort(key=lambda x: x['name'].lower())

            return {
                'success': True,
                'services': services_list,
                'raw_data': data,
                'error': None,
                'total_services': len(services_list)
            }

        except Exception as e:
            return {
                'success': False,
                'services': [],
                'raw_data': {},
                'error': str(e)
            }
