"""
Тестирование парсера внешних скриптов
"""

from src.utils.script_parser import ScriptParser

# Читаем тестовый скрипт
with open('test_external_script.py', 'r', encoding='utf-8') as f:
    script_code = f.read()

# Создаем парсер
parser = ScriptParser()

# Парсим скрипт
print("=" * 80)
print("ТЕСТИРОВАНИЕ ПАРСЕРА ВНЕШНИХ СКРИПТОВ")
print("=" * 80)

result = parser.parse_external_script(script_code)

print("\n1. ИЗВЛЕЧЕННЫЕ ДЕЙСТВИЯ:")
print("-" * 80)
for i, action in enumerate(result['actions'], 1):
    print(f"{i}. {action['type'].upper()}")
    if 'value' in action:
        print(f"   Значение: {action['value']}")
    if 'selector' in action:
        print(f"   Селектор: {action['selector']}")
    print()

print("\n2. ИЗВЛЕЧЕННЫЕ ЗНАЧЕНИЯ ДЛЯ ПАРАМЕТРИЗАЦИИ:")
print("-" * 80)
for i, value in enumerate(result['values'], 1):
    print(f"{i}. {value}")

print("\n3. ЗАГОЛОВКИ CSV:")
print("-" * 80)
print(", ".join(result['csv_headers']))

print("\n4. КОНВЕРТИРОВАННЫЙ КОД:")
print("-" * 80)
print(result['converted_code'])

print("\n5. CSV КОНТЕНТ (3 строки примеров):")
print("-" * 80)
csv_content = parser.generate_csv_content(num_rows=3)
print(csv_content)

print("\n" + "=" * 80)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("=" * 80)
