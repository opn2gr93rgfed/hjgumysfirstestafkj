"""
Менеджер для управления SMS провайдерами
"""
from typing import Dict, Optional, Type, List
from .base_provider import BaseSMSProvider
from .daisy_sms_provider import DaisySMSProvider


class ProviderManager:
    """
    Менеджер для работы с различными SMS провайдерами

    Позволяет регистрировать провайдеры, создавать их экземпляры
    и управлять активными подключениями.
    """

    # Реестр доступных провайдеров
    _providers: Dict[str, Type[BaseSMSProvider]] = {
        'daisysms': DaisySMSProvider,
        # Здесь можно добавить другие провайдеры в будущем:
        # 'sms-activate': SMSActivateProvider,
        # '5sim': FiveSimProvider,
        # и т.д.
    }

    def __init__(self):
        """Инициализация менеджера"""
        self._active_provider: Optional[BaseSMSProvider] = None
        self._provider_name: Optional[str] = None

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseSMSProvider]):
        """
        Зарегистрировать новый провайдер

        Args:
            name: Уникальное имя провайдера (например, 'daisysms')
            provider_class: Класс провайдера (наследник BaseSMSProvider)
        """
        if not issubclass(provider_class, BaseSMSProvider):
            raise ValueError(f"{provider_class} должен быть наследником BaseSMSProvider")

        cls._providers[name.lower()] = provider_class

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """
        Получить список доступных провайдеров

        Returns:
            Список имен провайдеров
        """
        return list(cls._providers.keys())

    def create_provider(self, provider_name: str, api_key: str, **kwargs) -> BaseSMSProvider:
        """
        Создать экземпляр провайдера

        Args:
            provider_name: Имя провайдера (например, 'daisysms')
            api_key: API ключ
            **kwargs: Дополнительные параметры для провайдера

        Returns:
            Экземпляр провайдера

        Raises:
            ValueError: Если провайдер не найден
        """
        provider_name = provider_name.lower()

        if provider_name not in self._providers:
            available = ', '.join(self._providers.keys())
            raise ValueError(
                f"Провайдер '{provider_name}' не найден. "
                f"Доступные провайдеры: {available}"
            )

        provider_class = self._providers[provider_name]
        provider = provider_class(api_key, **kwargs)

        # Сохраняем как активный провайдер
        self._active_provider = provider
        self._provider_name = provider_name

        return provider

    def get_active_provider(self) -> Optional[BaseSMSProvider]:
        """
        Получить активный провайдер

        Returns:
            Активный провайдер или None
        """
        return self._active_provider

    def get_provider_name(self) -> Optional[str]:
        """
        Получить имя активного провайдера

        Returns:
            Имя провайдера или None
        """
        return self._provider_name

    def disconnect(self):
        """Отключить активный провайдер"""
        self._active_provider = None
        self._provider_name = None

    def test_connection(self) -> Dict:
        """
        Проверить подключение к активному провайдеру

        Returns:
            Dict: {
                'connected': bool,
                'provider': str,
                'balance': float,
                'error': Optional[str]
            }
        """
        if not self._active_provider:
            return {
                'connected': False,
                'provider': None,
                'balance': 0.0,
                'error': 'Провайдер не подключен'
            }

        # Проверяем подключение через получение баланса
        balance_info = self._active_provider.get_balance()

        return {
            'connected': balance_info['success'],
            'provider': self._provider_name,
            'balance': balance_info.get('balance', 0.0),
            'error': balance_info.get('error')
        }
