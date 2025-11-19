"""
Движок шаблонов для замены переменных в коде
"""
import re
from typing import Dict, List, Tuple


class TemplateEngine:
    """Класс для работы с шаблонами и переменными"""

    # Паттерн для поиска переменных: {{variable_name}}
    VARIABLE_PATTERN = r'\{\{(\w+)\}\}'

    def __init__(self):
        """Инициализация движка шаблонов"""
        pass

    def find_variables(self, text: str) -> List[str]:
        """
        Найти все переменные в тексте

        Args:
            text: Текст для поиска

        Returns:
            Список названий переменных
        """
        matches = re.findall(self.VARIABLE_PATTERN, text)
        return list(set(matches))  # Уникальные значения

    def replace_variables(self, text: str, variables: Dict[str, str]) -> str:
        """
        Заменить переменные на значения

        Args:
            text: Текст с переменными
            variables: Словарь {имя_переменной: значение}

        Returns:
            Текст с замененными переменными
        """
        result = text

        for var_name, var_value in variables.items():
            pattern = r'\{\{' + var_name + r'\}\}'
            # Преобразуем значение в строку и экранируем кавычки
            value_str = str(var_value) if var_value is not None else ''
            result = re.sub(pattern, value_str, result)

        return result

    def validate_variables(self, text: str, available_columns: List[str]) -> Tuple[bool, List[str]]:
        """
        Проверить, что все переменные в тексте доступны в колонках

        Args:
            text: Текст с переменными
            available_columns: Список доступных колонок

        Returns:
            (True/False, список недостающих переменных)
        """
        found_variables = self.find_variables(text)
        missing_variables = [var for var in found_variables if var not in available_columns]

        return (len(missing_variables) == 0, missing_variables)

    def highlight_variables(self, text: str) -> str:
        """
        Подсветить переменные в тексте (для отображения в GUI)

        Args:
            text: Текст с переменными

        Returns:
            Текст с подсвеченными переменными
        """
        # Для GUI можно использовать специальные маркеры
        def highlight_match(match):
            return f"[VAR:{match.group(1)}]"

        return re.sub(self.VARIABLE_PATTERN, highlight_match, text)

    def get_variable_usage_count(self, text: str) -> Dict[str, int]:
        """
        Подсчитать количество использований каждой переменной

        Args:
            text: Текст с переменными

        Returns:
            Словарь {имя_переменной: количество_использований}
        """
        variables = re.findall(self.VARIABLE_PATTERN, text)
        usage_count = {}

        for var in variables:
            usage_count[var] = usage_count.get(var, 0) + 1

        return usage_count

    @staticmethod
    def escape_for_python_string(value: str) -> str:
        """
        Экранировать значение для использования в Python строке

        Args:
            value: Значение для экранирования

        Returns:
            Экранированное значение
        """
        if value is None:
            return ''

        # Экранируем обратные слеши и кавычки
        value = str(value)
        value = value.replace('\\', '\\\\')
        value = value.replace('"', '\\"')
        value = value.replace("'", "\\'")

        return value
