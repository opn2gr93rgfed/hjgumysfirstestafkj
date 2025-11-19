"""
Парсер для конвертации внешних Selenium скриптов в формат auto2tesst
Поддерживает импорт скриптов из Chrome Web Store расширений
"""

import re
from typing import Dict, List, Tuple, Optional


class ScriptParser:
    """Парсер для конвертации внешних скриптов"""

    def __init__(self):
        self.extracted_values = []  # Извлеченные значения для параметризации
        self.variable_names = []     # Имена переменных

    def parse_external_script(self, script_code: str) -> Dict:
        """
        Парсит внешний скрипт и извлекает действия

        Args:
            script_code: Исходный код скрипта

        Returns:
            Dict с информацией о скрипте:
            {
                'actions': [...],  # Список действий
                'values': [...],   # Извлеченные значения
                'csv_headers': [...],  # Заголовки для CSV
                'converted_code': '...'  # Конвертированный код
            }
        """
        self.extracted_values = []
        self.variable_names = []

        # Извлечь все действия из скрипта
        actions = self._extract_actions(script_code)

        # Оптимизировать действия (убрать избыточные клики)
        optimized_actions = self._optimize_actions(actions)

        # Извлечь значения для параметризации
        self._extract_values_from_actions(optimized_actions)

        # Сгенерировать конвертированный код
        converted_code = self._generate_converted_code(optimized_actions)

        # Получить URL (если есть)
        url = self._extract_url(script_code)

        return {
            'actions': optimized_actions,
            'values': self.extracted_values,
            'csv_headers': self.variable_names,
            'converted_code': converted_code,
            'url': url
        }

    def _extract_actions(self, script_code: str) -> List[Dict]:
        """Извлекает действия из скрипта"""
        actions = []
        lines = script_code.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()

            # Пропустить комментарии и пустые строки
            if not line or line.startswith('#'):
                continue

            # driver.get() - переход на страницу
            get_match = re.search(r'driver\.get\(["\'](.+?)["\']\)', line)
            if get_match:
                actions.append({
                    'type': 'navigate',
                    'url': get_match.group(1),
                    'line': i
                })
                continue

            # click() - клик
            click_match = re.search(r'driver\.find_element\((.+?)\)\.click\(\)', line)
            if click_match:
                selector = self._parse_selector(click_match.group(1))
                actions.append({
                    'type': 'click',
                    'selector': selector,
                    'line': i
                })
                continue

            # send_keys() - ввод текста
            sendkeys_match = re.search(r'driver\.find_element\((.+?)\)\.send_keys\(["\'](.+?)["\']\)', line)
            if sendkeys_match:
                selector = self._parse_selector(sendkeys_match.group(1))
                value = sendkeys_match.group(2)
                actions.append({
                    'type': 'type',
                    'selector': selector,
                    'value': value,
                    'line': i
                })
                continue

            # submit() - отправка формы
            submit_match = re.search(r'driver\.find_element\((.+?)\)\.submit\(\)', line)
            if submit_match:
                selector = self._parse_selector(submit_match.group(1))
                actions.append({
                    'type': 'submit',
                    'selector': selector,
                    'line': i
                })
                continue

        return actions

    def _parse_selector(self, selector_str: str) -> Dict:
        """
        Парсит селектор из разных форматов

        Поддерживает:
        - By.XPATH, "..."
        - By.ID, "..."
        - By.NAME, "..."
        - get_xpath(driver, 'ID')
        """
        selector_str = selector_str.strip()

        # Формат: get_xpath(driver, 'ID')
        getxpath_match = re.search(r'get_xpath\(driver,\s*["\'](.+?)["\']\)', selector_str)
        if getxpath_match:
            element_id = getxpath_match.group(1)
            return {
                'type': 'custom_xpath',
                'element_id': element_id,
                'by': 'By.XPATH',
                'selector': f'//custom[@id="{element_id}"]'  # Placeholder
            }

        # Формат: By.XPATH, "..."
        by_match = re.search(r'By\.(\w+),\s*["\'](.+?)["\']', selector_str)
        if by_match:
            by_type = by_match.group(1)
            selector_value = by_match.group(2)
            return {
                'type': by_type.lower(),
                'by': f'By.{by_type}',
                'selector': selector_value
            }

        # Если не удалось распарсить, вернуть как есть
        return {
            'type': 'unknown',
            'by': 'By.XPATH',
            'selector': '//unknown'
        }

    def _optimize_actions(self, actions: List[Dict]) -> List[Dict]:
        """
        Оптимизирует действия:
        - Убирает клики перед send_keys
        - Убирает дублирующиеся действия
        """
        optimized = []
        i = 0

        while i < len(actions):
            current = actions[i]
            next_action = actions[i + 1] if i + 1 < len(actions) else None

            # Если это клик и следующее - ввод текста, пропустить клик
            if (current['type'] == 'click' and
                next_action and
                next_action['type'] == 'type'):
                # Пропустить клик, он избыточен
                i += 1
                continue

            optimized.append(current)
            i += 1

        return optimized

    def _extract_values_from_actions(self, actions: List[Dict]):
        """Извлекает значения из действий для параметризации"""
        self.extracted_values = []
        self.variable_names = []

        for action in actions:
            if action['type'] == 'type' and 'value' in action:
                value = action['value']
                var_name = self._generate_variable_name(value, len(self.extracted_values))

                self.extracted_values.append(value)
                self.variable_names.append(var_name)

    def _generate_variable_name(self, value: str, index: int) -> str:
        """Генерирует имя переменной на основе значения"""
        # Определить тип значения
        if '@' in value and '.' in value:
            return 'email'

        if value.isdigit():
            if len(value) == 8:
                return 'date_of_birth'
            elif len(value) >= 10:
                return 'phone'
            else:
                return 'number'

        if ' ' in value:
            # Имя или фамилия
            parts = value.lower().split()
            if index == 0:
                return 'firstname'
            elif index == 1:
                return 'lastname'
            else:
                return 'fullname'

        # Если первое значение - вероятно firstname, второе - lastname
        if index == 0:
            return 'firstname'
        elif index == 1:
            return 'lastname'
        elif index == 2:
            return 'email'
        elif index == 3:
            return 'password'
        else:
            # Простое текстовое значение
            if len(value) <= 10:
                clean = re.sub(r'[^a-z0-9]', '', value.lower())
                if clean:
                    return clean[:10]
            return f'field_{index + 1}'

    def _generate_converted_code(self, actions: List[Dict]) -> str:
        """Генерирует конвертированный код"""
        code_lines = []

        # Проверить есть ли custom_xpath селекторы (требуют замены)
        has_custom_selectors = any(
            action.get('selector', {}).get('type') == 'custom_xpath'
            for action in actions
        )

        if has_custom_selectors:
            code_lines.append('# ⚠️ ВНИМАНИЕ! СЕЛЕКТОРЫ ТРЕБУЮТ ЗАМЕНЫ!')
            code_lines.append('#')
            code_lines.append('# Импортированный скрипт использует внутренние ID расширения,')
            code_lines.append('# которые НЕ РАБОТАЮТ напрямую. Вам нужно заменить селекторы')
            code_lines.append('# на реальные XPath/CSS/ID элементов.')
            code_lines.append('#')
            code_lines.append('# КАК НАЙТИ ПРАВИЛЬНЫЕ СЕЛЕКТОРЫ:')
            code_lines.append('# 1. Откройте страницу в браузере')
            code_lines.append('# 2. Нажмите F12 (DevTools)')
            code_lines.append('# 3. Нажмите Ctrl+Shift+C (инспектор элементов)')
            code_lines.append('# 4. Кликните на нужный элемент')
            code_lines.append('# 5. В DevTools правой кнопкой -> Copy -> Copy XPath (или Copy selector)')
            code_lines.append('# 6. Замените селектор ниже на скопированный')
            code_lines.append('#')
            code_lines.append('# ПРИОРИТЕТ СЕЛЕКТОРОВ (от лучшего к худшему):')
            code_lines.append('# 1. By.ID - если у элемента есть id="..."')
            code_lines.append('# 2. By.NAME - если у элемента есть name="..."')
            code_lines.append('# 3. By.CSS_SELECTOR - для простых классов')
            code_lines.append('# 4. By.XPATH - только если нет других вариантов')
            code_lines.append('#')
            code_lines.append('# ПРИМЕР ЗАМЕНЫ:')
            code_lines.append('# БЫЛО: (By.XPATH, "//custom[@id=\\"ABC123\\"]")')
            code_lines.append('# СТАЛО: (By.ID, "firstName")  # если у поля id="firstName"')
            code_lines.append('# ИЛИ:    (By.NAME, "first_name")  # если name="first_name"')
            code_lines.append('# ИЛИ:    (By.XPATH, "//input[@placeholder=\'First name\']")')
            code_lines.append('')

        # Добавить driver.get() в начало (если есть URL)
        if actions and actions[0].get('type') != 'navigate':
            code_lines.append('# Переход на страницу')
            code_lines.append('# ВАЖНО: Укажите правильный URL!')
            code_lines.append('driver.get("https://example.com")')
            code_lines.append('# Случайная задержка для имитации реального пользователя')
            code_lines.append('time.sleep(random.uniform(2, 4))')
            code_lines.append('')

        # Индекс для переменных
        var_index = 0

        for action in actions:
            if action['type'] == 'navigate':
                code_lines.append(f'# Переход на страницу')
                code_lines.append(f'driver.get("{action["url"]}")')
                code_lines.append(f'time.sleep(2)')
                code_lines.append('')

            elif action['type'] == 'click':
                selector_str = action["selector"]["selector"].replace('"', '\\"')

                # Добавить предупреждение если это custom селектор
                if action["selector"]["type"] == 'custom_xpath':
                    code_lines.append('# ⚠️ ЗАМЕНИТЕ этот селектор на реальный!')
                    code_lines.append('# Пример: (By.ID, "submitButton") или (By.NAME, "submit")')

                code_lines.append('# Клик по элементу')
                code_lines.append('# Увеличенный таймаут 30 сек для медленных прокси')
                code_lines.append('element = WebDriverWait(driver, 30).until(')
                code_lines.append(f'    EC.element_to_be_clickable(({action["selector"]["by"]}, "{selector_str}"))')
                code_lines.append(')')
                code_lines.append('element.click()')
                code_lines.append('print("[OK] Клик выполнен")')
                code_lines.append('# Случайная задержка 2-4 сек (антибот защита)')
                code_lines.append('time.sleep(random.uniform(2, 4))')
                code_lines.append('')

            elif action['type'] == 'type':
                var_name = self.variable_names[var_index] if var_index < len(self.variable_names) else f'field_{var_index + 1}'
                selector_str = action["selector"]["selector"].replace('"', '\\"')

                # Добавить предупреждение если это custom селектор
                if action["selector"]["type"] == 'custom_xpath':
                    code_lines.append(f'# ⚠️ ЗАМЕНИТЕ этот селектор на реальный!')
                    code_lines.append(f'# Это поле для ввода: {{{{{var_name}}}}}')
                    code_lines.append(f'# Пример: (By.ID, "{var_name}") или (By.NAME, "{var_name}")')

                code_lines.append(f'# Ввод текста: {{{{{var_name}}}}}')
                code_lines.append('# Увеличенный таймаут 30 сек для медленных прокси')
                code_lines.append('element = WebDriverWait(driver, 30).until(')
                code_lines.append(f'    EC.presence_of_element_located(({action["selector"]["by"]}, "{selector_str}"))')
                code_lines.append(')')
                code_lines.append(f'element.clear()  # Очистить поле перед вводом')
                code_lines.append(f'element.send_keys("{{{{{var_name}}}}}")')
                code_lines.append(f'print(f"[OK] Введено: {{{{{var_name}}}}}")')
                code_lines.append('# Случайная задержка 1.5-3 сек (имитация печати человеком)')
                code_lines.append('time.sleep(random.uniform(1.5, 3))')
                code_lines.append('')
                var_index += 1

            elif action['type'] == 'submit':
                selector_str = action["selector"]["selector"].replace('"', '\\"')

                # Добавить предупреждение если это custom селектор
                if action["selector"]["type"] == 'custom_xpath':
                    code_lines.append('# ⚠️ ЗАМЕНИТЕ этот селектор на реальный!')
                    code_lines.append('# Пример: (By.XPATH, "//button[@type=\'submit\']")')

                code_lines.append('# Отправка формы')
                code_lines.append('# Увеличенный таймаут 30 сек для медленных прокси')
                code_lines.append('element = WebDriverWait(driver, 30).until(')
                code_lines.append(f'    EC.presence_of_element_located(({action["selector"]["by"]}, "{selector_str}"))')
                code_lines.append(')')
                code_lines.append('element.submit()')
                code_lines.append('print("[OK] Форма отправлена")')
                code_lines.append('# Задержка 3-5 сек после отправки формы')
                code_lines.append('time.sleep(random.uniform(3, 5))')
                code_lines.append('')

        return '\n'.join(code_lines)

    def _extract_url(self, script_code: str) -> Optional[str]:
        """Извлекает URL из скрипта"""
        match = re.search(r'driver\.get\(["\'](.+?)["\']\)', script_code)
        if match:
            return match.group(1)
        return None

    def generate_csv_content(self, num_rows: int = 3) -> str:
        """
        Генерирует содержимое CSV файла с примерами данных

        Args:
            num_rows: Количество строк с данными

        Returns:
            Строка с содержимым CSV
        """
        if not self.variable_names:
            return ''

        # Заголовки
        csv_lines = [','.join(self.variable_names)]

        # Первая строка - оригинальные значения
        csv_lines.append(','.join(self.extracted_values))

        # Дополнительные строки с примерами
        for i in range(num_rows - 1):
            row_values = []
            for j, var_name in enumerate(self.variable_names):
                original_value = self.extracted_values[j] if j < len(self.extracted_values) else ''
                example_value = self._generate_example_value(var_name, original_value, i + 1)
                row_values.append(example_value)
            csv_lines.append(','.join(row_values))

        return '\n'.join(csv_lines)

    def _generate_example_value(self, var_name: str, original_value: str, index: int) -> str:
        """Генерирует примерное значение для CSV на основе типа переменной"""
        if var_name == 'email':
            return f'user{index}@example.com'
        elif var_name == 'firstname':
            names = ['John', 'Jane', 'Bob', 'Alice', 'Charlie']
            return names[index % len(names)]
        elif var_name == 'lastname':
            surnames = ['Smith', 'Doe', 'Johnson', 'Williams', 'Brown']
            return surnames[index % len(surnames)]
        elif var_name in ['password', 'date_of_birth', 'phone', 'number']:
            # Использовать оригинальное значение с модификацией
            if original_value.isdigit():
                try:
                    num = int(original_value) + index
                    return str(num)
                except:
                    return original_value
            return original_value
        else:
            return f'{original_value}_{index}' if original_value else f'value_{index}'
