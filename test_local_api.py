#!/usr/bin/env python3
"""Тест локального API Octobrowser"""

import requests

# UUID профиля из последнего запуска
profile_uuid = "bcc0f42472dc4b1a9a7c8482068e76b0"

print("=" * 70)
print("ТЕСТ: Попытка запуска профиля через ЛОКАЛЬНЫЙ API")
print("=" * 70)
print()

# Вариант 1: Локальный API (если Octobrowser запущен)
local_api_url = f"http://localhost:58888/api/v1/profiles/{profile_uuid}/start"

print(f"1. Попытка запуска через локальный API:")
print(f"   URL: {local_api_url}")

try:
    response = requests.post(local_api_url, json={}, timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    print()
except requests.exceptions.ConnectionError:
    print(f"   [ОШИБКА] Octobrowser не запущен или локальный API недоступен")
    print(f"   Решение: Запустите приложение Octobrowser на компьютере")
    print()
except Exception as e:
    print(f"   [ОШИБКА] {e}")
    print()

# Вариант 2: Облачный API (уже проверяли)
cloud_api_url = f"https://app.octobrowser.net/api/v2/automation/profiles/{profile_uuid}/start"

print(f"2. Попытка запуска через облачный API:")
print(f"   URL: {cloud_api_url}")
print(f"   Результат: 404 Not Found (как мы уже знаем)")
print()

print("=" * 70)
print("ВЫВОД:")
print("=" * 70)
print("Octobrowser использует ГИБРИДНУЮ архитектуру:")
print("  - Облачный API: управление профилями (создание, удаление, настройки)")
print("  - Локальный API: запуск браузеров (требует запущенный Octobrowser)")
print()
print("ЧТО НУЖНО СДЕЛАТЬ:")
print("  1. Запустить приложение Octobrowser на компьютере")
print("  2. Использовать локальный API endpoint для запуска профилей")
print("  3. Или использовать Quick Launch URL")
print()
