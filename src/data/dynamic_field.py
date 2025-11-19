"""
Система динамических полей для получения данных из SMS провайдеров
"""
from typing import Dict, Optional, Any, Callable, List
from enum import Enum


class FieldType(Enum):
    """Типы динамических полей"""
    STATIC = "static"           # Статическое значение
    PHONE_NUMBER = "phone"      # Номер телефона из SMS API
    OTP_CODE = "otp"            # OTP код из SMS API
    DYNAMIC = "dynamic"         # Другой динамический тип


class DynamicField:
    """
    Класс для представления динамического поля

    Динамическое поле может получать значение из различных источников:
    - Статическое значение
    - SMS API (номер телефона)
    - SMS API (OTP код)
    - Пользовательская функция
    """

    def __init__(
        self,
        name: str,
        field_type: FieldType = FieldType.STATIC,
        static_value: Optional[str] = None,
        value_provider: Optional[Callable] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Инициализация динамического поля

        Args:
            name: Имя поля (например, 'phone_number', 'otp_code')
            field_type: Тип поля
            static_value: Статическое значение (для STATIC типа)
            value_provider: Функция для получения значения
            metadata: Дополнительные метаданные
        """
        self.name = name
        self.field_type = field_type
        self.static_value = static_value
        self.value_provider = value_provider
        self.metadata = metadata or {}
        self._cached_value = None
        self._activation_id = None  # Для отслеживания SMS активации

    def get_value(self, context: Optional[Dict] = None) -> str:
        """
        Получить значение поля

        Args:
            context: Контекст для получения значения (например, SMS провайдер)

        Returns:
            Значение поля
        """
        if self.field_type == FieldType.STATIC:
            return self.static_value or ""

        elif self.field_type in [FieldType.PHONE_NUMBER, FieldType.OTP_CODE]:
            # Для динамических полей требуется провайдер
            if not context or 'sms_provider' not in context:
                raise ValueError(
                    f"Для поля '{self.name}' типа '{self.field_type.value}' "
                    "требуется SMS провайдер в контексте"
                )

            return self._get_from_sms_provider(context)

        elif self.field_type == FieldType.DYNAMIC:
            if self.value_provider:
                return self.value_provider(context)
            else:
                raise ValueError(f"Для динамического поля '{self.name}' не указан value_provider")

        return ""

    def _get_from_sms_provider(self, context: Dict) -> str:
        """
        Получить значение от SMS провайдера

        Args:
            context: Контекст с SMS провайдером

        Returns:
            Значение поля
        """
        sms_provider = context['sms_provider']
        service = context.get('service', 'ds')  # По умолчанию Discord

        if self.field_type == FieldType.PHONE_NUMBER:
            # Если уже есть кэшированное значение, вернуть его
            if self._cached_value and self._activation_id:
                return self._cached_value

            # Получить новый номер
            result = sms_provider.get_number(service, **self.metadata)

            if result['success']:
                self._cached_value = result['phone_number']
                self._activation_id = result['activation_id']
                return self._cached_value
            else:
                raise RuntimeError(f"Ошибка получения номера: {result.get('error')}")

        elif self.field_type == FieldType.OTP_CODE:
            # Для OTP нужен activation_id
            activation_id = context.get('activation_id') or self._activation_id

            if not activation_id:
                raise ValueError("Для получения OTP требуется activation_id")

            # Получить OTP код
            timeout = self.metadata.get('timeout', 180)
            result = sms_provider.get_sms_code(activation_id, timeout=timeout)

            if result['success']:
                self._cached_value = result['code']
                return self._cached_value
            else:
                raise RuntimeError(f"Ошибка получения OTP: {result.get('error')}")

        return ""

    def clear_cache(self):
        """Очистить кэшированное значение"""
        self._cached_value = None
        self._activation_id = None

    def get_activation_id(self) -> Optional[str]:
        """Получить ID активации (для OTP)"""
        return self._activation_id

    def to_dict(self) -> Dict:
        """
        Сериализовать в словарь

        Returns:
            Dict представление поля
        """
        return {
            'name': self.name,
            'field_type': self.field_type.value,
            'static_value': self.static_value,
            'metadata': self.metadata,
            'has_value_provider': self.value_provider is not None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'DynamicField':
        """
        Создать из словаря

        Args:
            data: Словарь с данными

        Returns:
            Экземпляр DynamicField
        """
        field_type = FieldType(data.get('field_type', 'static'))

        return cls(
            name=data['name'],
            field_type=field_type,
            static_value=data.get('static_value'),
            metadata=data.get('metadata', {})
        )


class DynamicFieldManager:
    """
    Менеджер для управления динамическими полями
    """

    def __init__(self):
        """Инициализация менеджера"""
        self.fields: Dict[str, DynamicField] = {}

    def add_field(self, field: DynamicField):
        """
        Добавить поле

        Args:
            field: Динамическое поле
        """
        self.fields[field.name] = field

    def get_field(self, name: str) -> Optional[DynamicField]:
        """
        Получить поле по имени

        Args:
            name: Имя поля

        Returns:
            Поле или None
        """
        return self.fields.get(name)

    def remove_field(self, name: str):
        """
        Удалить поле

        Args:
            name: Имя поля
        """
        if name in self.fields:
            del self.fields[name]

    def get_all_values(self, context: Optional[Dict] = None) -> Dict[str, str]:
        """
        Получить значения всех полей

        Args:
            context: Контекст для получения значений

        Returns:
            Словарь {имя_поля: значение}
        """
        values = {}

        for name, field in self.fields.items():
            try:
                values[name] = field.get_value(context)
            except Exception as e:
                # Логируем ошибку, но продолжаем
                print(f"Ошибка получения значения для поля '{name}': {e}")
                values[name] = ""

        return values

    def clear_all_caches(self):
        """Очистить все кэши"""
        for field in self.fields.values():
            field.clear_cache()

    def get_phone_fields(self) -> List[DynamicField]:
        """
        Получить все поля с номерами телефонов

        Returns:
            Список полей типа PHONE_NUMBER
        """
        return [
            field for field in self.fields.values()
            if field.field_type == FieldType.PHONE_NUMBER
        ]

    def get_otp_fields(self) -> List[DynamicField]:
        """
        Получить все поля с OTP кодами

        Returns:
            Список полей типа OTP_CODE
        """
        return [
            field for field in self.fields.values()
            if field.field_type == FieldType.OTP_CODE
        ]

    def to_dict(self) -> Dict:
        """
        Сериализовать все поля

        Returns:
            Dict со всеми полями
        """
        return {
            name: field.to_dict()
            for name, field in self.fields.items()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'DynamicFieldManager':
        """
        Создать менеджер из словаря

        Args:
            data: Словарь с полями

        Returns:
            Экземпляр DynamicFieldManager
        """
        manager = cls()

        for name, field_data in data.items():
            field = DynamicField.from_dict(field_data)
            manager.add_field(field)

        return manager
