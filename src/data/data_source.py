"""
Модуль для работы с источниками данных (CSV, Excel)
"""
import csv
from typing import List, Dict, Optional
from pathlib import Path


class DataSource:
    """Класс для работы с табличными данными"""

    def __init__(self, file_path: Optional[str] = None):
        """
        Инициализация источника данных

        Args:
            file_path: Путь к файлу с данными (CSV или Excel)
        """
        self.file_path = file_path
        self.data = []
        self.headers = []

        if file_path:
            self.load_data(file_path)

    def load_data(self, file_path: str):
        """
        Загрузка данных из файла

        Args:
            file_path: Путь к файлу

        Raises:
            ValueError: Если формат файла не поддерживается
        """
        self.file_path = file_path
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        # Определяем формат файла
        extension = file_path_obj.suffix.lower()

        if extension == '.csv':
            self._load_csv(file_path)
        elif extension in ['.xlsx', '.xls']:
            self._load_excel(file_path)
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {extension}")

    def _load_csv(self, file_path: str):
        """Загрузка CSV файла"""
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            self.headers = reader.fieldnames or []
            self.data = list(reader)

    def _load_excel(self, file_path: str):
        """Загрузка Excel файла"""
        try:
            import openpyxl
        except ImportError:
            raise ImportError("Для работы с Excel установите: pip install openpyxl")

        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

        # Первая строка - заголовки
        self.headers = [cell.value for cell in sheet[1] if cell.value]

        # Остальные строки - данные
        self.data = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if any(row):  # Пропускаем пустые строки
                row_dict = {}
                for i, header in enumerate(self.headers):
                    row_dict[header] = row[i] if i < len(row) else None
                self.data.append(row_dict)

    def get_headers(self) -> List[str]:
        """
        Получить список заголовков колонок

        Returns:
            Список заголовков
        """
        return self.headers

    def get_row(self, index: int) -> Dict:
        """
        Получить строку данных по индексу

        Args:
            index: Индекс строки

        Returns:
            Словарь с данными строки
        """
        if 0 <= index < len(self.data):
            return self.data[index]
        return {}

    def get_all_rows(self) -> List[Dict]:
        """
        Получить все строки данных

        Returns:
            Список словарей с данными
        """
        return self.data

    def get_row_count(self) -> int:
        """
        Получить количество строк данных

        Returns:
            Количество строк
        """
        return len(self.data)

    def get_column_values(self, column_name: str) -> List:
        """
        Получить все значения из колонки

        Args:
            column_name: Название колонки

        Returns:
            Список значений
        """
        return [row.get(column_name) for row in self.data if column_name in row]

    def create_sample_csv(self, output_path: str):
        """
        Создать пример CSV файла

        Args:
            output_path: Путь для сохранения
        """
        sample_data = [
            {'search_query': 'носки', 'quantity': '2', 'color': 'синий'},
            {'search_query': 'обувь', 'quantity': '1', 'color': 'черный'},
            {'search_query': 'штаны', 'quantity': '3', 'color': 'серый'},
        ]

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            if sample_data:
                writer = csv.DictWriter(f, fieldnames=sample_data[0].keys())
                writer.writeheader()
                writer.writerows(sample_data)
