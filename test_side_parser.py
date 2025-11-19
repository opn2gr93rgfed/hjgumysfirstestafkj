"""
Тестирование парсера Selenium IDE (.side файлов)
"""

from src.utils.selenium_ide_parser import SeleniumIDEParser

# Читаем тестовый .side файл
with open('test_selenium_ide.side', 'r', encoding='utf-8') as f:
    side_content = f.read()

# Создаем парсер
parser = SeleniumIDEParser()

print("=" * 80)
print("ТЕСТИРОВАНИЕ ПАРСЕРА SELENIUM IDE")
print("=" * 80)

try:
    result = parser.parse_side_file(side_content)

    print("\n1. БАЗОВЫЙ URL:")
    print("-" * 80)
    print(result['url'])

    print("\n2. ИЗВЛЕЧЕННЫЕ ДЕЙСТВИЯ:")
    print("-" * 80)
    for i, action in enumerate(result['actions'], 1):
        print(f"{i}. {action['type'].upper()}")
        if 'url' in action:
            print(f"   URL: {action['url']}")
        if 'selector' in action:
            print(f"   Селектор: {action['selector']['by']} = \"{action['selector']['selector']}\"")
        if 'value' in action:
            print(f"   Значение: {action['value']}")
        print()

    print("\n3. ИЗВЛЕЧЕННЫЕ ЗНАЧЕНИЯ ДЛЯ ПАРАМЕТРИЗАЦИИ:")
    print("-" * 80)
    for i, value in enumerate(result['values'], 1):
        print(f"{i}. {value}")

    print("\n4. ЗАГОЛОВКИ CSV:")
    print("-" * 80)
    print(", ".join(result['csv_headers']))

    print("\n5. КОНВЕРТИРОВАННЫЙ КОД:")
    print("-" * 80)
    print(result['converted_code'])

    print("\n6. CSV КОНТЕНТ (3 строки):")
    print("-" * 80)
    csv_content = parser.generate_csv_content(num_rows=3)
    print(csv_content)

    print("\n" + "=" * 80)
    print("ТЕСТИРОВАНИЕ УСПЕШНО ЗАВЕРШЕНО")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()
