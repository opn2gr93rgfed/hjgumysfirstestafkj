"""
Базовый абстрактный класс для SMS провайдеров
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from enum import Enum


class SMSStatus(Enum):
    """Статусы SMS активации"""
    WAITING = "waiting"          # Ожидание SMS
    RECEIVED = "received"        # SMS получено
    CANCELLED = "cancelled"      # Активация отменена
    TIMEOUT = "timeout"          # Истекло время ожидания
    ERROR = "error"              # Ошибка


class BaseSMSProvider(ABC):
    """
    Базовый класс для всех SMS провайдеров.

    Все провайдеры должны наследоваться от этого класса и реализовывать его методы.
    """

    def __init__(self, api_key: str, **kwargs):
        """
        Инициализация провайдера

        Args:
            api_key: API ключ для доступа к сервису
            **kwargs: Дополнительные параметры конфигурации
        """
        self.api_key = api_key
        self.config = kwargs
        self._active_activations = {}  # {activation_id: {...}}

    @abstractmethod
    def get_balance(self) -> Dict:
        """
        Получить баланс аккаунта

        Returns:
            Dict с информацией о балансе:
            {
                'balance': float,
                'currency': str,
                'success': bool,
                'error': Optional[str]
            }
        """
        pass

    @abstractmethod
    def get_services(self) -> Dict:
        """
        Получить список доступных сервисов

        Returns:
            Dict со списком сервисов:
            {
                'services': List[Dict],
                'success': bool,
                'error': Optional[str]
            }
        """
        pass

    @abstractmethod
    def get_number(self, service: str, **params) -> Dict:
        """
        Арендовать номер для получения SMS

        Args:
            service: Код сервиса (например, 'ds' для Discord)
            **params: Дополнительные параметры (страна, оператор и т.д.)

        Returns:
            Dict с информацией о номере:
            {
                'activation_id': str,
                'phone_number': str,
                'service': str,
                'success': bool,
                'error': Optional[str]
            }
        """
        pass

    @abstractmethod
    def get_sms_code(self, activation_id: str, timeout: int = 180) -> Dict:
        """
        Получить SMS код для активации

        Args:
            activation_id: ID активации (получен при аренде номера)
            timeout: Максимальное время ожидания в секундах

        Returns:
            Dict с кодом:
            {
                'code': str,
                'full_text': str,
                'status': SMSStatus,
                'success': bool,
                'error': Optional[str]
            }
        """
        pass

    @abstractmethod
    def cancel_activation(self, activation_id: str) -> Dict:
        """
        Отменить активацию и вернуть деньги

        Args:
            activation_id: ID активации

        Returns:
            Dict с результатом:
            {
                'success': bool,
                'error': Optional[str]
            }
        """
        pass

    @abstractmethod
    def finish_activation(self, activation_id: str) -> Dict:
        """
        Завершить активацию (подтвердить получение SMS)

        Args:
            activation_id: ID активации

        Returns:
            Dict с результатом:
            {
                'success': bool,
                'error': Optional[str]
            }
        """
        pass

    def get_provider_name(self) -> str:
        """
        Получить название провайдера

        Returns:
            Название провайдера
        """
        return self.__class__.__name__.replace('Provider', '')

    def get_active_activations(self) -> List[str]:
        """
        Получить список активных активаций

        Returns:
            Список ID активных активаций
        """
        return list(self._active_activations.keys())

    def _add_activation(self, activation_id: str, data: Dict):
        """Добавить активацию в список активных"""
        self._active_activations[activation_id] = data

    def _remove_activation(self, activation_id: str):
        """Удалить активацию из списка активных"""
        if activation_id in self._active_activations:
            del self._active_activations[activation_id]
