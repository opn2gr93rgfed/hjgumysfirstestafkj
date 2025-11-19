#!/usr/bin/env python3
"""Тест демонстрирующий проблему с HTTP статус-кодами"""

import json

# Симуляция ответа API
class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)

    def json(self):
        return self.json_data


# Реальный ответ Octobrowser API
api_response = {
    "success": True,
    "msg": "",
    "data": {"uuid": "1c75afa5284b4fd8bfa60212f7fc44d0"},
    "code": None
}

print("=" * 60)
print("ТЕСТ: Octobrowser API может возвращать код 201 вместо 200")
print("=" * 60)
print()

# Тест 1: API возвращает 200 OK
print("Тест 1: API возвращает 200 OK")
response = MockResponse(api_response, 200)
print(f"  Status Code: {response.status_code}")
print(f"  Старый код (== 200): {'✅ РАБОТАЕТ' if response.status_code == 200 else '❌ НЕ РАБОТАЕТ'}")
print(f"  Новый код (in [200, 201]): {'✅ РАБОТАЕТ' if response.status_code in [200, 201] else '❌ НЕ РАБОТАЕТ'}")
print()

# Тест 2: API возвращает 201 Created (стандарт REST для создания ресурсов)
print("Тест 2: API возвращает 201 Created (стандарт REST)")
response = MockResponse(api_response, 201)
print(f"  Status Code: {response.status_code}")
print(f"  Старый код (== 200): {'✅ РАБОТАЕТ' if response.status_code == 200 else '❌ НЕ РАБОТАЕТ'}")
print(f"  Новый код (in [200, 201]): {'✅ РАБОТАЕТ' if response.status_code in [200, 201] else '❌ НЕ РАБОТАЕТ'}")
print()

print("=" * 60)
print("ВЫВОД:")
print("=" * 60)
print("Если Octobrowser API возвращает 201 Created при создании профиля")
print("(что является стандартной практикой REST API), то старый код")
print("с проверкой 'status_code == 200' НЕ РАБОТАЕТ, даже если API")
print("вернул успешный ответ с данными!")
print()
print("Новый код с проверкой 'status_code in [200, 201]' работает")
print("в обоих случаях.")
print()
