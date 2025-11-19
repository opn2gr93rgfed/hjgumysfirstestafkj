#!/usr/bin/env python3
"""
Octobrowser Script Builder - LEGACY UI (Tkinter)
Запуск старого интерфейса если CustomTkinter не работает
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from src.gui.main_window import main

if __name__ == "__main__":
    print("="*60)
    print("Octobrowser Script Builder - LEGACY UI")
    print("="*60)
    print("⚠️  Запущена старая версия интерфейса (Tkinter)")
    print("💡 Для современного UI установите: pip install -r requirements.txt")
    print("="*60)
    print()

    try:
        main()
    except KeyboardInterrupt:
        print("\nПриложение остановлено пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
