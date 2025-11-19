# Network Parser - Руководство по использованию

**Ветка: `claude/network-parser-01A2Wa64hwUdKUY14cYQRoXt`**

## Описание

Эта ветка содержит функционал для автоматизации с парсингом данных из Network вкладки браузера (Developer Tools). Система перехватывает HTTP responses в реальном времени и извлекает нужные данные для сохранения в CSV.

### Основные возможности

- 📊 **Работа с CSV данными** - чтение статических данных из CSV файла
- 🔍 **Перехват Network requests/responses** - автоматический перехват через Playwright
- 📡 **Парсинг JSON responses** - извлечение данных из API responses
- 💾 **Сохранение результатов в CSV** - автоматическое обновление CSV с результатами
- 🎯 **Поддержка нескольких вкладок** - перехват данных со всех открытых вкладок
- 🔧 **Кастомные парсеры** - возможность создавать свои функции парсинга

---

## Структура проекта

```
auto2tesst/
├── data/
│   ├── test_data.csv                     # CSV с входными данными
│   └── network_responses_*.json          # Захваченные Network responses (для отладки)
├── scripts/
│   └── automation_with_network_parser.py # Главный скрипт автоматизации
├── src/
│   └── utils/
│       ├── csv_manager.py                # Модуль работы с CSV
│       └── network_parser.py             # Модуль перехвата Network данных
└── NETWORK_PARSER_GUIDE.md              # Это руководство
```

---

## Установка и настройка

### 1. Установите зависимости

```bash
pip install playwright
playwright install chromium
```

### 2. Подготовьте CSV файл

Создайте файл `data/test_data.csv` со следующими колонками:

```csv
zip_code,first_name,last_name,email,phone,address,birth_month,birth_day,birth_year,gender,education,quote_id,premium_price,carrier_name,policy_url,status,execution_date
33071,Jamie,Walter,test@gmail.com,3156257735,2077 W Atlantic Blvd,01,20,1964,Male,High School/GED,,,,,pending,
```

**Обязательные поля для ввода:**
- `zip_code` - почтовый индекс
- `first_name` - имя
- `last_name` - фамилия
- `email` - электронная почта
- `phone` - телефон (10 цифр)
- `address` - адрес
- `birth_month` - месяц рождения (01-12)
- `birth_day` - день рождения (01-31)
- `birth_year` - год рождения (YYYY)
- `gender` - пол (Male/Female)
- `education` - образование
- `status` - статус записи (pending/completed/failed)

**Поля для результатов (заполняются автоматически):**
- `quote_id` - ID котировки из Network response
- `premium_price` - цена премиума
- `carrier_name` - название страховой компании
- `policy_url` - URL полиса
- `execution_date` - дата выполнения

---

## Использование

### Запуск автоматизации

```bash
python scripts/automation_with_network_parser.py
```

**Что происходит:**
1. Скрипт читает первую строку со статусом `pending` из CSV
2. Запускает браузер и начинает автоматизацию
3. Перехватывает все Network responses в фоновом режиме
4. Выполняет все действия с использованием данных из CSV
5. Парсит нужные данные из перехваченных responses
6. Сохраняет результаты обратно в CSV
7. Обновляет статус строки на `completed`
8. Сохраняет все responses в JSON файл для отладки

---

## Работа с CSV Manager

### Основные методы

```python
from src.utils.csv_manager import CSVManager

# Инициализация
csv_manager = CSVManager("data/test_data.csv")

# Получить следующую pending строку
data_row = csv_manager.get_next_pending_row()
# Возвращает: {'zip_code': '33071', 'first_name': 'Jamie', ...}

# Получить индекс текущей строки
row_index = csv_manager.current_row_index

# Обновить строку
csv_manager.update_row(row_index, {
    'quote_id': 'ABC123',
    'premium_price': '125.50'
})

# Отметить как выполненную
csv_manager.mark_as_completed(row_index, {
    'quote_id': 'ABC123',
    'premium_price': '125.50',
    'carrier_name': 'Sample Insurance'
})

# Отметить как проваленную
csv_manager.mark_as_failed(row_index, "Ошибка: таймаут")

# Получить количество pending записей
pending_count = csv_manager.get_all_pending_count()

# Форматировать телефон
formatted = csv_manager.format_phone("3156257735")
# Возвращает: "(315) 625-7735"
```

---

## Работа с Network Parser

### Инициализация и подключение

```python
from playwright.sync_api import sync_playwright
from src.utils.network_parser import NetworkParser

# Создаем парсер
network_parser = NetworkParser()

# Добавляем фильтры для URL которые хотим перехватывать
network_parser.add_filter(r'.*api.*quote.*')  # Все URL содержащие "api" и "quote"
network_parser.add_filter(r'.*policy.*')      # Все URL содержащие "policy"

# Подключаем к странице Playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    # Подключаем парсер
    network_parser.attach_to_page(page)

    # Теперь все responses будут перехватываться
    page.goto("https://example.com")
```

### Извлечение данных

```python
# Получить все захваченные responses
all_responses = network_parser.get_all_responses()

# Найти responses по URL паттерну
quote_responses = network_parser.find_responses_by_url(r'.*api/quote.*')

# Извлечь конкретное поле из JSON
quote_id = network_parser.extract_json_field(r'.*quote.*', 'quote_id')
price = network_parser.extract_json_field(r'.*quote.*', 'data.premium.price')

# Сохранить все responses в файл (для отладки)
network_parser.save_responses_to_file('responses.json')

# Очистить захваченные responses
network_parser.clear_responses()
```

### Кастомные парсеры

Вы можете создать свои функции для парсинга специфичных responses:

```python
def my_custom_parser(response_data: dict) -> dict:
    """
    Кастомный парсер для извлечения нужных данных

    response_data содержит:
    - url: URL запроса
    - status: HTTP статус
    - headers: HTTP заголовки
    - body: Текст ответа
    - json: Распарсенный JSON (если ответ в JSON формате)
    """
    result = {}

    if response_data.get('json'):
        json_data = response_data['json']

        # Извлекаем нужные поля
        result['my_field'] = json_data.get('some_field')
        result['nested_field'] = json_data.get('data', {}).get('nested', {}).get('field')

    return result

# Использование кастомного парсера
network_parser.add_filter(r'.*api/custom.*', my_custom_parser)
```

### Примеры парсинга

**Пример 1: Простое извлечение поля**

```python
# Response: {"quote_id": "ABC123", "premium": 125.50}
quote_id = network_parser.extract_json_field(r'.*quote.*', 'quote_id')
# Результат: "ABC123"
```

**Пример 2: Вложенные поля**

```python
# Response: {"data": {"quote": {"id": "ABC123", "premium": {"price": 125.50}}}}
price = network_parser.extract_json_field(r'.*quote.*', 'data.quote.premium.price')
# Результат: 125.50
```

**Пример 3: Множественные попытки извлечения**

```python
# Пробуем разные пути пока не найдем
quote_id = network_parser.extract_json_field(r'.*quote.*', 'quote_id')
if not quote_id:
    quote_id = network_parser.extract_json_field(r'.*quote.*', 'id')
if not quote_id:
    quote_id = network_parser.extract_json_field(r'.*quote.*', 'data.id')
```

---

## Поддержка нескольких вкладок

Network Parser автоматически работает с несколькими вкладками:

```python
# Основная страница
page = context.new_page()
network_parser.attach_to_page(page)

# Открытие новой вкладки
with page.expect_popup() as page1_info:
    page.get_by_role("button", name="Open new tab").click()
page1 = page1_info.value

# Подключаем парсер к новой вкладке
network_parser.attach_to_page(page1)

# Открытие третьей вкладки
with page1.expect_popup() as page2_info:
    page1.get_by_role("button", name="Continue").click()
page2 = page2_info.value

# Подключаем парсер к третьей вкладке
network_parser.attach_to_page(page2)

# Теперь парсер перехватывает responses со ВСЕХ трех вкладок
```

---

## Отладка

### Сохранение Network данных

Все перехваченные responses автоматически сохраняются в JSON файл:

```
data/network_responses_20241118_143052.json
```

Этот файл содержит:
- URL каждого запроса
- HTTP статус
- Headers
- Body (текст)
- JSON (если response был в JSON формате)
- Parsed (если использовался кастомный парсер)

### Просмотр захваченных данных

```python
# Вывести все захваченные URL
for resp in network_parser.get_all_responses():
    print(f"URL: {resp['url']}")
    print(f"Status: {resp['status']}")
    if resp.get('json'):
        print(f"JSON: {resp['json']}")
    print("-" * 60)
```

### Поиск конкретных данных

```python
# Найти все responses с определенным паттерном
api_responses = network_parser.find_responses_by_url(r'.*api.*')

for resp in api_responses:
    print(f"URL: {resp['url']}")
    if resp.get('json'):
        print(json.dumps(resp['json'], indent=2))
```

---

## Примеры использования

### Пример 1: Базовое использование

```python
from playwright.sync_api import sync_playwright
from src.utils.csv_manager import CSVManager
from src.utils.network_parser import NetworkParser

# Инициализация
csv_manager = CSVManager("data/test_data.csv")
network_parser = NetworkParser()

# Добавляем фильтры
network_parser.add_filter(r'.*api/quote.*')

# Получаем данные из CSV
data_row = csv_manager.get_next_pending_row()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Подключаем парсер
    network_parser.attach_to_page(page)

    # Автоматизация
    page.goto("https://example.com")
    page.fill("#email", data_row['email'])
    page.click("button[type='submit']")

    # Извлекаем данные
    quote_id = network_parser.extract_json_field(r'.*quote.*', 'id')

    # Сохраняем в CSV
    csv_manager.mark_as_completed(csv_manager.current_row_index, {
        'quote_id': quote_id
    })

    browser.close()
```

### Пример 2: Обработка нескольких записей

```python
csv_manager = CSVManager("data/test_data.csv")

while True:
    # Получаем следующую pending запись
    data_row = csv_manager.get_next_pending_row()

    if not data_row:
        print("Все записи обработаны!")
        break

    row_index = csv_manager.current_row_index

    try:
        # Выполняем автоматизацию
        run_automation(data_row)

        # Сохраняем результаты
        csv_manager.mark_as_completed(row_index, results)

    except Exception as e:
        # Отмечаем как проваленную
        csv_manager.mark_as_failed(row_index, str(e))
```

---

## FAQ

### Как добавить новые поля в CSV?

1. Откройте `data/test_data.csv`
2. Добавьте новые колонки в header
3. Заполните данные в строках
4. Используйте новые поля в скрипте: `data_row['new_field']`

### Как извлечь данные из сложного JSON?

Используйте точечную нотацию:

```python
# JSON: {"data": {"user": {"profile": {"name": "John"}}}}
name = network_parser.extract_json_field(r'.*api.*', 'data.user.profile.name')
```

### Что если нужно перехватить все запросы?

```python
# Универсальный фильтр для всех URL
network_parser.add_filter(r'.*')
```

### Как обработать ошибки в автоматизации?

```python
try:
    # Автоматизация
    run_automation(data_row)
    csv_manager.mark_as_completed(row_index, results)

except TimeoutError:
    csv_manager.mark_as_failed(row_index, "Timeout error")

except Exception as e:
    csv_manager.mark_as_failed(row_index, f"Error: {str(e)}")
```

### Как сохранить дополнительные данные?

```python
# Добавьте любые поля в словарь результатов
result_data = {
    'quote_id': quote_id,
    'premium_price': price,
    'carrier_name': carrier,
    'custom_field_1': value1,
    'custom_field_2': value2,
}

csv_manager.mark_as_completed(row_index, result_data)
```

---

## Ограничения

1. **Без SMS/OTP функционала** - эта ветка работает только со статическими данными из CSV
2. **Только Playwright** - используется Playwright, а не Selenium
3. **Chromium only** - работает только с Chromium браузером
4. **Синхронный режим** - скрипт обрабатывает по одной записи за раз

---

## Troubleshooting

### Ошибка: "CSV файл не найден"

Убедитесь что файл `data/test_data.csv` существует и путь правильный.

### Не перехватываются responses

1. Проверьте что парсер подключен к странице: `network_parser.attach_to_page(page)`
2. Проверьте фильтры URL - возможно паттерн неправильный
3. Сохраните все responses в файл и проверьте: `network_parser.save_responses_to_file()`

### Не находит данные в JSON

1. Сохраните responses в файл и посмотрите структуру JSON
2. Проверьте правильность пути к полю: `'data.field.subfield'`
3. Используйте множественные попытки с разными путями

### Браузер не запускается

```bash
# Переустановите Playwright
playwright install chromium
```

---

## Примеры реальных сценариев

### Сценарий 1: Извлечение Quote ID и цены

```python
# Ищем quote_id в разных местах
quote_id = network_parser.extract_json_field(r'.*quote.*', 'quote_id') or \
           network_parser.extract_json_field(r'.*quote.*', 'id') or \
           network_parser.extract_json_field(r'.*quote.*', 'data.quote_id')

# Ищем цену
price = network_parser.extract_json_field(r'.*quote.*', 'premium_price') or \
        network_parser.extract_json_field(r'.*quote.*', 'premium') or \
        network_parser.extract_json_field(r'.*quote.*', 'data.premium.amount')
```

### Сценарий 2: Обработка пагинации CSV

```python
processed_count = 0
max_records = 10

while processed_count < max_records:
    data_row = csv_manager.get_next_pending_row()
    if not data_row:
        break

    # Обработка...
    processed_count += 1

print(f"Обработано: {processed_count} записей")
```

---

## Дополнительная информация

### Полезные ссылки

- [Playwright Documentation](https://playwright.dev/python/)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Regex тестирование](https://regex101.com/)

### Структура Response объекта

```python
{
    'url': 'https://api.example.com/quote',
    'status': 200,
    'headers': {'content-type': 'application/json', ...},
    'body': '{"quote_id": "ABC123", ...}',
    'json': {'quote_id': 'ABC123', ...},
    'parsed': {'custom_field': 'value'}  # Если использовался кастомный парсер
}
```

---

**Автор:** Claude AI
**Ветка:** `claude/network-parser-01A2Wa64hwUdKUY14cYQRoXt`
**Дата создания:** 2024-11-18
