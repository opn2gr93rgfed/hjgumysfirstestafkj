"""
CSV Manager - модуль для работы с CSV файлами данных
Используется для чтения статических данных и записи результатов автоматизации
"""

import csv
import os
from datetime import datetime
from typing import Dict, List, Optional


class CSVManager:
    """Класс для управления CSV данными"""

    def __init__(self, csv_file_path: str):
        """
        Инициализация менеджера CSV

        Args:
            csv_file_path: Путь к CSV файлу
        """
        self.csv_file_path = csv_file_path
        self.current_row_index = 0

        # Проверяем существование файла
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"CSV файл не найден: {csv_file_path}")

    def get_next_pending_row(self) -> Optional[Dict]:
        """
        Получить следующую строку со статусом 'pending'

        Returns:
            Dict с данными строки или None если нет pending строк
        """
        rows = self._read_all_rows()

        for index, row in enumerate(rows):
            if row.get('status', '').strip().lower() == 'pending':
                self.current_row_index = index
                return row

        return None

    def update_row(self, row_index: int, update_data: Dict) -> bool:
        """
        Обновить строку в CSV файле

        Args:
            row_index: Индекс строки для обновления
            update_data: Словарь с данными для обновления

        Returns:
            True если успешно, False если ошибка
        """
        try:
            rows = self._read_all_rows()

            if row_index >= len(rows):
                return False

            # Обновляем данные строки
            rows[row_index].update(update_data)

            # Добавляем дату выполнения если её нет
            if 'execution_date' in rows[row_index]:
                rows[row_index]['execution_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Записываем обратно в файл
            self._write_all_rows(rows)
            return True

        except Exception as e:
            print(f"Ошибка обновления CSV: {e}")
            return False

    def mark_as_completed(self, row_index: int, result_data: Dict) -> bool:
        """
        Отметить строку как выполненную и сохранить результаты

        Args:
            row_index: Индекс строки
            result_data: Данные результата (quote_id, premium_price, etc.)

        Returns:
            True если успешно
        """
        result_data['status'] = 'completed'
        return self.update_row(row_index, result_data)

    def mark_as_failed(self, row_index: int, error_message: str = '') -> bool:
        """
        Отметить строку как проваленную

        Args:
            row_index: Индекс строки
            error_message: Сообщение об ошибке

        Returns:
            True если успешно
        """
        return self.update_row(row_index, {
            'status': 'failed',
            'error_message': error_message
        })

    def _read_all_rows(self) -> List[Dict]:
        """Прочитать все строки из CSV файла"""
        rows = []

        with open(self.csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        return rows

    def _write_all_rows(self, rows: List[Dict]) -> None:
        """Записать все строки в CSV файл"""
        if not rows:
            return

        fieldnames = rows[0].keys()

        with open(self.csv_file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def get_all_pending_count(self) -> int:
        """Получить количество pending записей"""
        rows = self._read_all_rows()
        return sum(1 for row in rows if row.get('status', '').strip().lower() == 'pending')

    def format_phone(self, phone: str) -> str:
        """
        Форматировать телефон в формат (XXX) XXX-XXXX

        Args:
            phone: Номер телефона (только цифры)

        Returns:
            Отформатированный номер
        """
        # Убираем все нецифровые символы
        digits = ''.join(filter(str.isdigit, phone))

        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

        return phone
