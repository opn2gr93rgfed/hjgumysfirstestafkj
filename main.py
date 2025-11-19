#!/usr/bin/env python3
"""
Octobrowser Script Builder - Конструктор скриптов автоматизации
Главная точка входа приложения
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from src.gui.modern_main_window_v3 import main

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 auto2tesst v3.0 EPIC - Ultimate Playwright Automation")
    print("=" * 80)
    print("✨ Powered by CustomTkinter")
    print("🎨 Step-by-Step Workflow UI")
    print("📱 Toast Notifications & Smart Templates")
    print("🧪 Built-in API Testing")
    print("⌨️  Hotkeys: Ctrl+I (Import), Ctrl+R (Run), Esc (Stop)")
    print("=" * 80)
    print()

    try:
        main()
    except KeyboardInterrupt:
        print("\n✋ Приложение остановлено пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
