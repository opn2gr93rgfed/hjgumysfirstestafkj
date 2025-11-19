"""
Парсер для Selenium IDE (.side) файлов
Конвертирует формат Selenium IDE в код auto2tesst
"""

import json
import re
from typing import Dict, List, Optional


class SeleniumIDEParser:
    """Парсер для формата Selenium IDE (.side JSON)"""

    def __init__(self):
        self.extracted_values = []  # Извлеченные значения для параметризации
        self.variable_names = []     # Имена переменных

    def parse_side_file(self, side_content: str) -> Dict:
        """
        Парсит .side файл Selenium IDE

        Args:
            side_content: Содержимое .side файла (JSON)

        Returns:
            Dict с информацией:
            {
                'url': '...',
                'actions': [...],
                'values': [...],
                'csv_headers': [...],
                'converted_code': '...'
            }
        """
        try:
            data = json.loads(side_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Неверный формат JSON: {e}")

        # Получить базовый URL
        base_url = data.get('url', data.get('urls', [''])[0] if 'urls' in data else '')

        # Получить первый тест
        tests = data.get('tests', [])
        if not tests:
            raise ValueError("В файле нет тестов")

        test = tests[0]
        commands = test.get('commands', [])

        # Конвертировать команды в действия
        actions = self._convert_commands_to_actions(commands, base_url)

        # Оптимизировать действия
        optimized_actions = self._optimize_actions(actions)

        # Извлечь значения для параметризации
        self._extract_values_from_actions(optimized_actions)

        # Сгенерировать код
        converted_code = self._generate_converted_code(optimized_actions, base_url)

        return {
            'url': base_url,
            'actions': optimized_actions,
            'values': self.extracted_values,
            'csv_headers': self.variable_names,
            'converted_code': converted_code
        }

    def _convert_commands_to_actions(self, commands: List[Dict], base_url: str) -> List[Dict]:
        """Конвертирует команды Selenium IDE в действия"""
        actions = []

        for cmd in commands:
            command = cmd.get('command', '')
            target = cmd.get('target', '')
            targets = cmd.get('targets', [])
            value = cmd.get('value', '')

            # Пропустить некоторые команды
            if command in ['setWindowSize', 'mouseOver', 'mouseOut']:
                continue

            # open - переход на страницу
            if command == 'open':
                url = base_url + target if target.startswith('/') else target
                actions.append({
                    'type': 'navigate',
                    'url': url
                })

            # click - клик по элементу
            elif command == 'click':
                selector = self._parse_best_selector(target, targets)
                if selector:
                    actions.append({
                        'type': 'click',
                        'selector': selector
                    })

            # type - ввод текста
            elif command == 'type':
                selector = self._parse_best_selector(target, targets)
                if selector and value:
                    actions.append({
                        'type': 'type',
                        'selector': selector,
                        'value': value
                    })

            # sendKeys - тоже ввод текста
            elif command == 'sendKeys':
                selector = self._parse_best_selector(target, targets)
                if selector and value:
                    actions.append({
                        'type': 'type',
                        'selector': selector,
                        'value': value
                    })

            # submit - отправка формы
            elif command == 'submit':
                selector = self._parse_best_selector(target, targets)
                if selector:
                    actions.append({
                        'type': 'submit',
                        'selector': selector
                    })

        return actions

    def _parse_best_selector(self, target: str, targets: List) -> Optional[Dict]:
        """
        Выбирает лучший селектор из доступных

        Приоритет:
        1. id=... (By.ID)
        2. name=... (By.NAME)
        3. css=... (By.CSS_SELECTOR)
        4. xpath=... (By.XPATH)
        """
        # Список всех возможных селекторов
        all_selectors = [target] + [t[0] if isinstance(t, list) else t for t in targets]

        # Приоритет 1: ID
        for sel in all_selectors:
            if sel.startswith('id='):
                return {
                    'type': 'id',
                    'by': 'By.ID',
                    'selector': sel[3:]
                }

        # Приоритет 2: NAME
        for sel in all_selectors:
            if sel.startswith('name='):
                return {
                    'type': 'name',
                    'by': 'By.NAME',
                    'selector': sel[5:]
                }

        # Приоритет 3: CSS (простой, без экранирования)
        for sel in all_selectors:
            if sel.startswith('css='):
                css = sel[4:]
                # Избегать сложных CSS с nth-child
                if ':nth-child' not in css and ':nth-of-type' not in css:
                    return {
                        'type': 'css',
                        'by': 'By.CSS_SELECTOR',
                        'selector': css
                    }

        # Приоритет 4: XPath (простой)
        for sel in all_selectors:
            if sel.startswith('xpath='):
                xpath = sel[6:]
                # Предпочитаем XPath с атрибутами вместо позиционных
                if '@id' in xpath or '@name' in xpath or '@type' in xpath:
                    return {
                        'type': 'xpath',
                        'by': 'By.XPATH',
                        'selector': xpath
                    }

        # Приоритет 5: Любой CSS
        for sel in all_selectors:
            if sel.startswith('css='):
                return {
                    'type': 'css',
                    'by': 'By.CSS_SELECTOR',
                    'selector': sel[4:]
                }

        # Приоритет 6: Любой XPath
        for sel in all_selectors:
            if sel.startswith('xpath='):
                return {
                    'type': 'xpath',
                    'by': 'By.XPATH',
                    'selector': sel[6:]
                }

        # Если ничего не нашли, вернуть первый селектор как CSS
        if target:
            return {
                'type': 'css',
                'by': 'By.CSS_SELECTOR',
                'selector': target
            }

        return None

    def _optimize_actions(self, actions: List[Dict]) -> List[Dict]:
        """Оптимизирует действия"""
        optimized = []
        i = 0

        while i < len(actions):
            current = actions[i]
            next_action = actions[i + 1] if i + 1 < len(actions) else None

            # Объединить последовательные type в одно поле
            if current['type'] == 'type':
                # Найти все последующие type к тому же полю
                j = i + 1
                final_value = current['value']

                while (j < len(actions) and
                       actions[j]['type'] == 'type' and
                       actions[j]['selector']['selector'] == current['selector']['selector']):
                    final_value = actions[j]['value']  # Берем последнее значение
                    j += 1

                optimized.append({
                    **current,
                    'value': final_value
                })
                i = j
                continue

            # Пропустить клики перед вводом текста
            if (current['type'] == 'click' and
                next_action and
                next_action['type'] == 'type'):
                i += 1
                continue

            optimized.append(current)
            i += 1

        return optimized

    def _extract_values_from_actions(self, actions: List[Dict]):
        """Извлекает значения для параметризации"""
        self.extracted_values = []
        self.variable_names = []

        for action in actions:
            if action['type'] == 'type' and 'value' in action:
                value = action['value']
                var_name = self._generate_variable_name(value, len(self.extracted_values))

                self.extracted_values.append(value)
                self.variable_names.append(var_name)

    def _generate_variable_name(self, value: str, index: int) -> str:
        """Генерирует имя переменной"""
        # Email
        if '@' in value and '.' in value:
            return 'email'

        # Дата (формат DD / MM / YYYY)
        if re.match(r'\d{1,2}\s*/\s*\d{1,2}\s*/\s*\d{4}', value):
            return 'date_of_birth'

        # Число
        if value.replace(' ', '').replace('/', '').isdigit():
            if len(value) == 8:
                return 'date_of_birth'
            elif len(value) >= 10:
                return 'phone'
            else:
                return 'number'

        # Имена по порядку
        if index == 0:
            return 'firstname'
        elif index == 1:
            return 'lastname'
        elif index == 2 and '@' not in value:
            return 'username'
        else:
            # Чистое имя переменной из значения
            clean = re.sub(r'[^a-z0-9]', '', value.lower())
            if clean and len(clean) <= 15:
                return clean[:15]
            return f'field_{index + 1}'

    def _generate_converted_code(self, actions: List[Dict], base_url: str) -> str:
        """Генерирует Python код"""
        code_lines = []
        var_index = 0

        for action in actions:
            if action['type'] == 'navigate':
                code_lines.append('# Переход на страницу')
                code_lines.append(f'driver.get("{action["url"]}")')
                code_lines.append('time.sleep(random.uniform(2, 4))')
                code_lines.append('')

            elif action['type'] == 'click':
                selector = action['selector']
                selector_str = selector['selector'].replace('"', '\\"')

                code_lines.append('# Клик по элементу')
                code_lines.append(f'print(f"DEBUG: Поиск элемента для клика: {selector["by"]}, \\"{selector_str}\\"")')
                code_lines.append('element = WebDriverWait(driver, 30).until(')
                code_lines.append(f'    EC.element_to_be_clickable(({selector["by"]}, "{selector_str}"))')
                code_lines.append(')')
                code_lines.append('element.click()')
                code_lines.append('print("[OK] Клик выполнен")')
                code_lines.append('# Увеличенная задержка после клика для загрузки новой страницы/элементов')
                code_lines.append('time.sleep(random.uniform(3, 6))')
                code_lines.append('')

            elif action['type'] == 'type':
                selector = action['selector']
                selector_str = selector['selector'].replace('"', '\\"')
                var_name = self.variable_names[var_index] if var_index < len(self.variable_names) else f'field_{var_index + 1}'

                code_lines.append(f'# Ввод текста: {var_name}')
                code_lines.append(f'print(f"DEBUG: Поиск элемента для ввода {var_name}: {selector["by"]}, \\"{selector_str}\\"")')
                code_lines.append('element = WebDriverWait(driver, 30).until(')
                code_lines.append(f'    EC.presence_of_element_located(({selector["by"]}, "{selector_str}"))')
                code_lines.append(')')
                code_lines.append('element.clear()')
                code_lines.append(f'element.send_keys(data_row["{var_name}"])')
                code_lines.append(f'print(f"[OK] Введено {{data_row[\'{var_name}\']}}")')
                code_lines.append('time.sleep(random.uniform(1.5, 3))')
                code_lines.append('')
                var_index += 1

            elif action['type'] == 'submit':
                selector = action['selector']
                selector_str = selector['selector'].replace('"', '\\"')

                code_lines.append('# Отправка формы')
                code_lines.append(f'print(f"DEBUG: Поиск формы для отправки: {selector["by"]}, \\"{selector_str}\\"")')
                code_lines.append('element = WebDriverWait(driver, 30).until(')
                code_lines.append(f'    EC.presence_of_element_located(({selector["by"]}, "{selector_str}"))')
                code_lines.append(')')
                code_lines.append('element.submit()')
                code_lines.append('print("[OK] Форма отправлена")')
                code_lines.append('time.sleep(random.uniform(3, 5))')
                code_lines.append('')

        return '\n'.join(code_lines)

    def generate_csv_content(self, num_rows: int = 3) -> str:
        """Генерирует CSV контент"""
        if not self.variable_names:
            return ''

        csv_lines = [','.join(self.variable_names)]
        csv_lines.append(','.join(self.extracted_values))

        # Дополнительные строки
        for i in range(num_rows - 1):
            row_values = []
            for j, var_name in enumerate(self.variable_names):
                original_value = self.extracted_values[j] if j < len(self.extracted_values) else ''
                example_value = self._generate_example_value(var_name, original_value, i + 1)
                row_values.append(example_value)
            csv_lines.append(','.join(row_values))

        return '\n'.join(csv_lines)

    def _generate_example_value(self, var_name: str, original_value: str, index: int) -> str:
        """Генерирует примерное значение для CSV"""
        if var_name == 'email':
            return f'user{index}@example.com'
        elif var_name == 'firstname':
            names = ['John', 'Jane', 'Bob', 'Alice', 'Charlie']
            return names[index % len(names)]
        elif var_name == 'lastname':
            surnames = ['Smith', 'Doe', 'Johnson', 'Williams', 'Brown']
            return surnames[index % len(surnames)]
        elif var_name == 'date_of_birth':
            # Изменить дату
            if '/' in original_value:
                parts = original_value.split('/')
                if len(parts) == 3:
                    day = parts[0].strip()
                    month = parts[1].strip()
                    year = int(parts[2].strip()) + index
                    return f'{day} / {month} / {year}'
            return original_value
        else:
            return f'{original_value}_{index}' if original_value else f'value_{index}'
