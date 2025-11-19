#!/usr/bin/env python3
"""Тест запуска профиля через командную строку Octobrowser"""

import subprocess
import os

profile_uuid = "bcc0f42472dc4b1a9a7c8482068e76b0"

print("=" * 70)
print("ТЕСТ: Запуск профиля через CLI Octobrowser")
print("=" * 70)
print()

# Возможные пути к Octobrowser
octobrowser_paths = [
    r"C:\Program Files\Octo Browser\Octo Browser.exe",
    r"C:\Program Files (x86)\Octo Browser\Octo Browser.exe",
    r"C:\Users\admin\AppData\Local\Programs\Octo Browser\Octo Browser.exe",
]

print("Поиск Octobrowser...")
octo_exe = None
for path in octobrowser_paths:
    if os.path.exists(path):
        print(f"✓ Найден: {path}")
        octo_exe = path
        break
    else:
        print(f"✗ Не найден: {path}")

if not octo_exe:
    print("\n[ОШИБКА] Octobrowser не найден")
    print("Укажите правильный путь к Octo Browser.exe")
    exit(1)

print(f"\nПопытка запуска профиля {profile_uuid}...")
print(f"Команда: \"{octo_exe}\" --profile-id={profile_uuid}")
print()

# Пробуем запустить
try:
    # Вариант 1: С профилем ID
    subprocess.Popen([octo_exe, f"--profile-id={profile_uuid}"])
    print("✓ Профиль запущен через CLI")
    print("\nПОДСКАЗКА:")
    print("  Если профиль запустился, используйте этот метод в скриптах")
    print("  Для Selenium подключения используйте стандартный debug port")
except Exception as e:
    print(f"✗ Ошибка: {e}")
