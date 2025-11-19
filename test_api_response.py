#!/usr/bin/env python3
"""Тестовый скрипт для проверки парсинга ответов API"""

import json

# Симулируем ответ API
class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)

    def json(self):
        return self.json_data

# Тестируем с реальным ответом, который показал пользователь
response = MockResponse({
    "success": True,
    "msg": "",
    "data": {"uuid": "1c75afa5284b4fd8bfa60212f7fc44d0"},
    "code": None
})

print(f"=== Тест парсинга ответа API ===")
print(f"response.status_code = {response.status_code}")
print(f"response.text = {response.text}")
print()

if response.status_code == 200:
    result = response.json()

    # === ОТЛАДКА ===
    print(f"DEBUG: type(result) = {type(result)}")
    print(f"DEBUG: result.keys() = {result.keys() if isinstance(result, dict) else 'NOT A DICT'}")
    print(f"DEBUG: 'data' in result = {'data' in result if isinstance(result, dict) else False}")
    print(f"DEBUG: result.get('data') = {result.get('data') if isinstance(result, dict) else None}")
    print(f"DEBUG: Full result = {result}")
    print()

    # API возвращает структуру: {"success": true, "data": {"uuid": "..."}}
    if isinstance(result, dict) and 'data' in result and result['data'] and 'uuid' in result['data']:
        uuid = result['data']['uuid']
        print(f"✅ УСПЕХ! Профиль создан: {uuid}")
    else:
        print(f"❌ ОШИБКА! Ошибка создания профиля: {response.text}")
else:
    print(f"❌ HTTP ERROR: {response.status_code}")
