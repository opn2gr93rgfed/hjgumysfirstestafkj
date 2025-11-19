"""
Утилиты для обнаружения номеров телефонов и OTP кодов в скриптах
"""
import re
from typing import List, Dict, Optional, Tuple


class PhoneAndOTPDetector:
    """
    Класс для автоматического обнаружения полей номеров телефонов и OTP кодов
    """

    # Паттерны для определения номеров телефонов
    PHONE_PATTERNS = [
        r'\b\d{10}\b',                          # 10 цифр подряд (7653301209)
        r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # 765-330-1209 или 765.330.1209
        r'\+\d{1,3}[-.\s]?\d{10}',              # +1-7653301209
        r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',      # (765) 330-1209
    ]

    # Паттерны для определения OTP/кодов
    OTP_PATTERNS = [
        r'\b\d{4}\b',    # 4 цифры
        r'\b\d{5}\b',    # 5 цифр
        r'\b\d{6}\b',    # 6 цифр (самый популярный)
        r'\b\d{7}\b',    # 7 цифр
        r'\b\d{8}\b',    # 8 цифр
    ]

    # Ключевые слова для определения полей номера
    PHONE_KEYWORDS = [
        'phone', 'mobile', 'tel', 'telephone', 'cell',
        'номер', 'телефон', 'мобильный', 'сотовый',
        'number'
    ]

    # Ключевые слова для определения полей OTP
    OTP_KEYWORDS = [
        'otp', 'code', 'verification', 'confirm', 'sms',
        'код', 'верификация', 'подтверждение', 'смс',
        'verify', 'pin', 'token', 'security'
    ]

    @classmethod
    def detect_phone_number(cls, value: str) -> bool:
        """
        Определить, является ли значение номером телефона

        Args:
            value: Строка для проверки

        Returns:
            True если похоже на номер телефона
        """
        if not value or not isinstance(value, str):
            return False

        value = value.strip()

        # Проверяем по паттернам
        for pattern in cls.PHONE_PATTERNS:
            if re.match(pattern, value):
                return True

        return False

    @classmethod
    def detect_otp_code(cls, value: str) -> bool:
        """
        Определить, является ли значение OTP кодом

        Args:
            value: Строка для проверки

        Returns:
            True если похоже на OTP код
        """
        if not value or not isinstance(value, str):
            return False

        value = value.strip()

        # OTP обычно 4-8 цифр
        if re.match(r'^\d{4,8}$', value):
            # Дополнительная проверка - не слишком ли длинный для OTP
            if len(value) <= 8:
                return True

        return False

    @classmethod
    def detect_field_type_by_label(cls, label: str) -> Optional[str]:
        """
        Определить тип поля по его метке/имени

        Args:
            label: Метка поля (name, id, aria-label и т.д.)

        Returns:
            'phone', 'otp' или None
        """
        if not label or not isinstance(label, str):
            return None

        label_lower = label.lower()

        # Проверяем ключевые слова для телефона
        for keyword in cls.PHONE_KEYWORDS:
            if keyword in label_lower:
                return 'phone'

        # Проверяем ключевые слова для OTP
        for keyword in cls.OTP_KEYWORDS:
            if keyword in label_lower:
                return 'otp'

        return None

    @classmethod
    def analyze_script_data(cls, values: List[str], labels: Optional[List[str]] = None) -> Dict:
        """
        Проанализировать данные из скрипта и определить типы полей

        Args:
            values: Список значений из скрипта
            labels: Необязательный список меток полей

        Returns:
            Dict с результатами анализа:
            {
                'fields': [
                    {
                        'index': int,
                        'value': str,
                        'type': 'phone'|'otp'|'unknown',
                        'confidence': float,
                        'label': Optional[str]
                    },
                    ...
                ],
                'phone_indices': List[int],
                'otp_indices': List[int]
            }
        """
        fields = []
        phone_indices = []
        otp_indices = []

        for i, value in enumerate(values):
            field_type = 'unknown'
            confidence = 0.0
            label = labels[i] if labels and i < len(labels) else None

            # Сначала проверяем по метке (если есть)
            if label:
                label_type = cls.detect_field_type_by_label(label)
                if label_type:
                    field_type = label_type
                    confidence = 0.8  # Высокая уверенность по метке

            # Если тип не определен по метке, проверяем по значению
            if field_type == 'unknown':
                if cls.detect_phone_number(value):
                    field_type = 'phone'
                    confidence = 0.9  # Очень высокая уверенность
                elif cls.detect_otp_code(value):
                    field_type = 'otp'
                    confidence = 0.7  # Средняя уверенность (может быть и другим числом)

            fields.append({
                'index': i,
                'value': value,
                'type': field_type,
                'confidence': confidence,
                'label': label
            })

            if field_type == 'phone':
                phone_indices.append(i)
            elif field_type == 'otp':
                otp_indices.append(i)

        return {
            'fields': fields,
            'phone_indices': phone_indices,
            'otp_indices': otp_indices
        }

    @classmethod
    def suggest_field_names(cls, fields: List[Dict]) -> Dict[int, str]:
        """
        Предложить имена переменных для полей

        Args:
            fields: Список полей из analyze_script_data

        Returns:
            Dict: {index: suggested_name}
        """
        suggestions = {}
        phone_count = 0
        otp_count = 0

        for field in fields:
            index = field['index']
            field_type = field['type']

            if field_type == 'phone':
                phone_count += 1
                if phone_count == 1:
                    suggestions[index] = 'phone_number'
                else:
                    suggestions[index] = f'phone_number_{phone_count}'

            elif field_type == 'otp':
                otp_count += 1
                if otp_count == 1:
                    suggestions[index] = 'otp_code'
                else:
                    suggestions[index] = f'otp_code_{otp_count}'

        return suggestions


class FieldValidator:
    """
    Класс для валидации и ручной маркировки полей
    """

    @staticmethod
    def validate_phone_number(phone: str) -> Tuple[bool, Optional[str]]:
        """
        Валидация номера телефона

        Args:
            phone: Номер телефона

        Returns:
            (is_valid, error_message)
        """
        if not phone:
            return False, "Номер телефона не может быть пустым"

        # Удаляем все кроме цифр
        digits_only = re.sub(r'\D', '', phone)

        # Минимум 10 цифр
        if len(digits_only) < 10:
            return False, f"Слишком короткий номер ({len(digits_only)} цифр)"

        # Максимум 15 цифр (международный стандарт E.164)
        if len(digits_only) > 15:
            return False, f"Слишком длинный номер ({len(digits_only)} цифр)"

        return True, None

    @staticmethod
    def validate_otp_code(otp: str) -> Tuple[bool, Optional[str]]:
        """
        Валидация OTP кода

        Args:
            otp: OTP код

        Returns:
            (is_valid, error_message)
        """
        if not otp:
            return False, "OTP код не может быть пустым"

        # OTP должен содержать только цифры
        if not otp.isdigit():
            return False, "OTP должен содержать только цифры"

        # Обычно OTP это 4-8 цифр
        if len(otp) < 4:
            return False, f"OTP слишком короткий ({len(otp)} цифр)"

        if len(otp) > 8:
            return False, f"OTP слишком длинный ({len(otp)} цифр)"

        return True, None

    @staticmethod
    def format_phone_number(phone: str, format_type: str = 'digits_only') -> str:
        """
        Форматировать номер телефона

        Args:
            phone: Номер телефона
            format_type: Тип форматирования ('digits_only', 'international', 'us')

        Returns:
            Отформатированный номер
        """
        # Удаляем все кроме цифр
        digits = re.sub(r'\D', '', phone)

        if format_type == 'digits_only':
            return digits

        elif format_type == 'international' and len(digits) >= 10:
            # +1 (765) 330-1209
            country_code = digits[:-10] or '1'
            area = digits[-10:-7]
            prefix = digits[-7:-4]
            line = digits[-4:]
            return f"+{country_code} ({area}) {prefix}-{line}"

        elif format_type == 'us' and len(digits) == 10:
            # (765) 330-1209
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

        return digits
