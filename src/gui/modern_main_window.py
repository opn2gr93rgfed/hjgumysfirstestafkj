"""
🚀 auto2tesst v2 - Modern Main Window
Самый стильный Playwright-автотестер 2025 года

Powered by CustomTkinter + современный дизайн
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import json
import os
import threading
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Literal

# Импорты из проекта
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.octobrowser_api import OctobrowserAPI
from src.generator.script_generator import ScriptGenerator
from src.generator.playwright_script_generator import PlaywrightScriptGenerator
from src.runner.script_runner import ScriptRunner
from src.utils.script_parser import ScriptParser
from src.utils.selenium_ide_parser import SeleniumIDEParser
from src.utils.playwright_parser import PlaywrightParser
from src.sms.provider_manager import ProviderManager
from src.data.dynamic_field import DynamicFieldManager

# Modern UI Components
from .themes import ModernTheme, ButtonStyles
# Прямой импорт компонентов чтобы избежать загрузки новых v3 компонентов
from .components.toast import ToastManager
from .components.collapsible_frame import CollapsibleFrame


class ModernApp(ctk.CTk):
    """
    🎨 Главное приложение auto2tesst v2
    
    Современный минималистичный дизайн с:
    - Сайдбаром для навигации
    - Toast-уведомлениями
    - Collapsible секциями
    - Drag & Drop
    - Горячими клавишами
    - Цветовой подсветкой логов
    """

    def __init__(self):
        super().__init__()

        # === НАСТРОЙКИ ОКНА ===
        self.title("auto2tesst v2.0 - Modern Playwright Automation")
        self.geometry("1600x1000")
        self.minsize(1200, 700)

        # === ТЕМА ===
        ctk.set_appearance_mode("dark")  # dark/light
        ctk.set_default_color_theme("blue")  # blue/green/dark-blue
        
        self.current_theme = 'dark'
        self.theme = ModernTheme.DARK

        # === ДАННЫЕ ===
        self.config = {}
        self.load_config()

        # === КОМПОНЕНТЫ ===
        self.api: Optional[OctobrowserAPI] = None
        self.generator = ScriptGenerator()
        self.playwright_generator = PlaywrightScriptGenerator()
        self.runner = ScriptRunner()
        self.runner.set_output_callback(self.append_log)
        self.parser = ScriptParser()
        self.side_parser = SeleniumIDEParser()
        # PlaywrightParser с поддержкой OTP (передаем otp_enabled из конфига)
        otp_enabled = self.config.get('otp', {}).get('enabled', False)
        self.playwright_parser = PlaywrightParser(otp_enabled=otp_enabled)
        if not otp_enabled:
            print("[OTP] OTP handler disabled by config")
        self.sms_provider_manager = ProviderManager()
        self.dynamic_field_manager = DynamicFieldManager()

        # Данные импорта
        self.imported_data = None
        self.csv_data_rows = []

        # === ПЕРЕМЕННЫЕ UI ===
        self.current_page = "import"  # import, run, logs, settings
        
        # === СОЗДАНИЕ UI ===
        self.create_ui()

        # === TOAST MANAGER ===
        self.toast = ToastManager(self)
        self.toast.place_container(relx=0.98, rely=0.98, anchor="se")

        # === ГОРЯЧИЕ КЛАВИШИ ===
        self.setup_hotkeys()

        # === DRAG & DROP ===
        self.setup_drag_drop()

        # Показать приветствие
        self.after(500, lambda: self.toast.info("Добро пожаловать в auto2tesst v2! 🚀", duration=4000))

    # ========================================================================
    # КОНФИГУРАЦИЯ
    # ========================================================================

    def load_config(self):
        """Загрузка конфигурации из config.json"""
        config_path = Path(__file__).parent.parent.parent / 'config.json'
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Дефолтная конфигурация
            self.config = {
                'octobrowser': {'api_base_url': 'https://app.octobrowser.net/api/v2/automation', 'api_token': ''},
                'sms': {'provider': 'daisysms', 'api_key': '', 'service': 'ds'},
                'proxy': {'enabled': False, 'type': 'http', 'host': '', 'port': '', 'login': '', 'password': ''},
                'ui_settings': {'last_csv_path': '', 'automation_framework': 'playwright', 'playwright_target': 'library'},
                'script_settings': {'output_directory': 'generated_scripts', 'default_automation_framework': 'playwright'}
            }

    def save_config(self):
        """Сохранение конфигурации в config.json"""
        config_path = Path(__file__).parent.parent.parent / 'config.json'
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.toast.success("Настройки сохранены")
        except Exception as e:
            self.toast.error(f"Ошибка сохранения: {e}")

    # ========================================================================
    # СОЗДАНИЕ UI
    # ========================================================================

    def create_ui(self):
        """Создание всего интерфейса"""
        # 🔥 Конфигурация grid с правильными weights
        self.grid_rowconfigure(0, weight=0)     # Topbar - фиксированная высота
        self.grid_rowconfigure(1, weight=1)     # Main area - растягивается
        self.grid_columnconfigure(0, weight=0)  # Sidebar - фиксированная ширина
        self.grid_columnconfigure(1, weight=1)  # Main content - растягивается

        # === ВЕРХНЯЯ ПАНЕЛЬ ===
        self.create_top_bar()

        # === САЙДБАР ===
        self.create_sidebar()

        # === ГЛАВНАЯ ОБЛАСТЬ ===
        self.create_main_area()

    def create_top_bar(self):
        """Верхняя панель с заголовком и темой"""
        topbar = ctk.CTkFrame(
            self,
            height=60,
            corner_radius=0,
            fg_color=self.theme['bg_sidebar'],
            border_width=0,
            border_color=self.theme['border_primary'],
        )
        topbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        topbar.grid_columnconfigure(1, weight=1)
        topbar.grid_propagate(False)

        # Логотип + заголовок
        title_frame = ctk.CTkFrame(topbar, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        logo = ctk.CTkLabel(
            title_frame,
            text="🤖",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_hero']),
        )
        logo.pack(side="left", padx=(0, 12))

        title_col = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_col.pack(side="left")

        title = ctk.CTkLabel(
            title_col,
            text="auto2tesst",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_xxl'], 'bold'),
            text_color=self.theme['text_primary'],
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_col,
            text="Modern Playwright Automation Builder",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_sm']),
            text_color=self.theme['text_secondary'],
        )
        subtitle.pack(anchor="w")

        # Версия
        version = ctk.CTkLabel(
            topbar,
            text="v2.0",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_sm']),
            text_color=self.theme['accent_primary'],
        )
        version.grid(row=0, column=1, padx=20, sticky="e")

        # Переключатель темы
        theme_switch = ctk.CTkSegmentedButton(
            topbar,
            values=["🌙 Dark", "☀️ Light"],
            command=self.toggle_theme,
            fg_color=self.theme['bg_tertiary'],
            selected_color=self.theme['accent_primary'],
            selected_hover_color=self.theme['bg_hover'],
            unselected_color=self.theme['bg_tertiary'],
            unselected_hover_color=self.theme['bg_hover'],
            border_width=0,
            corner_radius=ModernTheme.RADIUS['lg'],
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_sm']),
        )
        theme_switch.grid(row=0, column=2, padx=20, pady=10, sticky="e")
        theme_switch.set("🌙 Dark")
        self.theme_switch = theme_switch

    def create_sidebar(self):
        """Сайдбар с навигацией"""
        sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=self.theme['bg_sidebar'],
            border_width=1,
            border_color=self.theme['border_primary'],
        )
        sidebar.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        sidebar.grid_propagate(False)

        # Кнопки навигации
        nav_buttons = [
            ("📥 Import Code", "import"),
            ("▶️ Run Script", "run"),
            ("📋 Logs", "logs"),
            ("⚙️ Settings", "settings"),
        ]

        for i, (text, page_id) in enumerate(nav_buttons):
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=lambda p=page_id: self.switch_page(p),
                height=48,
                corner_radius=ModernTheme.RADIUS['md'],
                fg_color="transparent",
                hover_color=self.theme['bg_hover'],
                text_color=self.theme['text_secondary'],
                anchor="w",
                font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_md'], 'bold'),
                border_width=0,
            )
            btn.grid(row=i, column=0, padx=12, pady=(12 if i == 0 else 4, 4), sticky="ew")

            # Сохранить ссылку на кнопки
            if not hasattr(self, 'nav_buttons'):
                self.nav_buttons = {}
            self.nav_buttons[page_id] = btn

        # Активировать первую кнопку
        self.nav_buttons["import"].configure(
            fg_color=self.theme['accent_primary'],
            text_color=self.theme['text_on_accent'],
        )

        self.sidebar = sidebar

    def create_main_area(self):
        """Главная область (переключаемые страницы)"""
        main = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=self.theme['bg_primary'],
        )
        main.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(0, weight=1)

        # === СТРАНИЦЫ ===
        self.pages = {}

        # Страница Import
        self.pages["import"] = self.create_import_page(main)
        self.pages["import"].grid(row=0, column=0, sticky="nsew")

        # Страница Run
        self.pages["run"] = self.create_run_page(main)
        
        # Страница Logs
        self.pages["logs"] = self.create_logs_page(main)

        # Страница Settings
        self.pages["settings"] = self.create_settings_page(main)

        # Показать первую страницу
        self.switch_page("import")

        self.main = main

    # ========================================================================
    # СТРАНИЦЫ
    # ========================================================================

    def create_import_page(self, parent):
        """Страница Import Code"""
        page = ctk.CTkFrame(parent, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        # Заголовок
        header = ctk.CTkLabel(
            page,
            text="📥 Import Playwright Code",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_xxl'], 'bold'),
            text_color=self.theme['text_primary'],
            anchor="w",
        )
        header.grid(row=0, column=0, padx=32, pady=(32, 16), sticky="ew")

        # Главный контейнер
        container = ctk.CTkFrame(
            page,
            corner_radius=ModernTheme.RADIUS['xl'],
            fg_color=self.theme['bg_secondary'],
            border_width=1,
            border_color=self.theme['border_primary'],
        )
        container.grid(row=1, column=0, padx=32, pady=(0, 32), sticky="nsew")
        # 🔥 Правильные weights для адаптивного layout
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=0)  # Кнопки - фиксированная высота
        container.grid_rowconfigure(1, weight=0)  # Label - фиксированная высота
        container.grid_rowconfigure(2, weight=1)  # Code editor - растягивается

        # Кнопки импорта
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.grid(row=0, column=0, padx=24, pady=24, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        import_file_btn = ctk.CTkButton(
            btn_frame,
            text="📂 Open Python File",
            command=self.import_from_file,
            height=56,
            corner_radius=ModernTheme.RADIUS['xl'],
            fg_color=self.theme['accent_primary'],
            hover_color=self.theme['bg_hover'],
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_lg'], 'bold'),
        )
        import_file_btn.grid(row=0, column=0, padx=(0, 12), sticky="ew")

        import_clipboard_btn = ctk.CTkButton(
            btn_frame,
            text="📋 Paste from Clipboard",
            command=self.import_from_clipboard,
            height=56,
            corner_radius=ModernTheme.RADIUS['xl'],
            fg_color=self.theme['accent_secondary'],
            hover_color=self.theme['bg_hover'],
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_lg'], 'bold'),
        )
        import_clipboard_btn.grid(row=0, column=1, padx=(12, 0), sticky="ew")

        # Редактор кода
        editor_label = ctk.CTkLabel(
            container,
            text="Imported Code Preview:",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_md'], 'bold'),
            text_color=self.theme['text_secondary'],
            anchor="w",
        )
        editor_label.grid(row=1, column=0, padx=24, pady=(0, 8), sticky="w")

        self.code_editor = ctk.CTkTextbox(
            container,
            corner_radius=ModernTheme.RADIUS['lg'],
            fg_color=self.theme['bg_tertiary'],
            border_width=1,
            border_color=self.theme['border_primary'],
            text_color=self.theme['text_primary'],
            font=('Consolas', 12),
            wrap="none",
        )
        self.code_editor.grid(row=2, column=0, padx=24, pady=(0, 24), sticky="nsew")

        # Drag & Drop зона
        drop_zone = ctk.CTkLabel(
            self.code_editor,
            text="📎 Drag & Drop .py file here",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_lg']),
            text_color=self.theme['text_tertiary'],
        )
        drop_zone.place(relx=0.5, rely=0.5, anchor="center")
        self.drop_zone_label = drop_zone

        return page

    def create_run_page(self, parent):
        """Страница Run Script"""
        page = ctk.CTkFrame(parent, fg_color="transparent")
        # 🔥 Правильные weights для адаптивного layout
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(0, weight=0)  # Header - фиксированная высота
        page.grid_rowconfigure(1, weight=0)  # Control panel - фиксированная высота
        page.grid_rowconfigure(2, weight=1)  # Log container - растягивается

        # Заголовок
        header = ctk.CTkLabel(
            page,
            text="▶️ Run Script",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_xxl'], 'bold'),
            text_color=self.theme['text_primary'],
            anchor="w",
        )
        header.grid(row=0, column=0, padx=32, pady=(32, 16), sticky="ew")

        # Панель управления
        control_panel = ctk.CTkFrame(
            page,
            corner_radius=ModernTheme.RADIUS['xl'],
            fg_color=self.theme['bg_secondary'],
            border_width=1,
            border_color=self.theme['border_primary'],
            height=120,
        )
        control_panel.grid(row=1, column=0, padx=32, pady=(0, 16), sticky="ew")
        control_panel.grid_propagate(False)
        control_panel.grid_columnconfigure((0, 1, 2), weight=1)

        # Кнопка Start
        self.start_btn = ctk.CTkButton(
            control_panel,
            text="▶️ START",
            command=self.start_script,
            height=72,
            corner_radius=ModernTheme.RADIUS['xl'],
            fg_color=self.theme['accent_success'],
            hover_color=self.theme['bg_hover'],
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_xl'], 'bold'),
        )
        self.start_btn.grid(row=0, column=0, padx=24, pady=24, sticky="ew")

        # Кнопка Stop
        self.stop_btn = ctk.CTkButton(
            control_panel,
            text="⏹️ STOP",
            command=self.stop_script,
            height=72,
            corner_radius=ModernTheme.RADIUS['xl'],
            fg_color=self.theme['accent_error'],
            hover_color=self.theme['bg_hover'],
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_xl'], 'bold'),
            state="disabled",
        )
        self.stop_btn.grid(row=0, column=1, padx=(0, 24), pady=24, sticky="ew")

        # Прогресс
        progress_frame = ctk.CTkFrame(control_panel, fg_color="transparent")
        progress_frame.grid(row=0, column=2, padx=(0, 24), pady=24, sticky="nsew")

        progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to run",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_md']),
            text_color=self.theme['text_secondary'],
        )
        progress_label.pack(pady=(8, 4))

        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            corner_radius=ModernTheme.RADIUS['full'],
            height=12,
            fg_color=self.theme['bg_tertiary'],
            progress_color=self.theme['accent_primary'],
        )
        self.progress_bar.pack(fill="x", pady=4)
        self.progress_bar.set(0)

        self.progress_label = progress_label

        # Лог выполнения
        log_container = ctk.CTkFrame(
            page,
            corner_radius=ModernTheme.RADIUS['xl'],
            fg_color=self.theme['bg_secondary'],
            border_width=1,
            border_color=self.theme['border_primary'],
        )
        log_container.grid(row=2, column=0, padx=32, pady=(0, 32), sticky="nsew")
        # 🔥 Правильные weights для адаптивного layout
        log_container.grid_columnconfigure(0, weight=1)
        log_container.grid_rowconfigure(0, weight=0)  # Header - фиксированная высота
        log_container.grid_rowconfigure(1, weight=1)  # Log textbox - растягивается

        log_header = ctk.CTkLabel(
            log_container,
            text="📋 Execution Log:",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_md'], 'bold'),
            text_color=self.theme['text_secondary'],
            anchor="w",
        )
        log_header.grid(row=0, column=0, padx=24, pady=(24, 8), sticky="w")

        self.run_log = ctk.CTkTextbox(
            log_container,
            corner_radius=ModernTheme.RADIUS['lg'],
            fg_color=self.theme['bg_tertiary'],
            border_width=0,
            text_color=self.theme['text_primary'],
            font=('Consolas', 11),
            wrap="word",
        )
        self.run_log.grid(row=1, column=0, padx=24, pady=(0, 24), sticky="nsew")

        return page

    def create_logs_page(self, parent):
        """Страница Logs (дубликат run log с фильтрами)"""
        page = ctk.CTkFrame(parent, fg_color="transparent")
        # 🔥 Правильные weights для адаптивного layout
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(0, weight=0)  # Header - фиксированная высота
        page.grid_rowconfigure(1, weight=1)  # Log container - растягивается

        header = ctk.CTkLabel(
            page,
            text="📋 All Logs",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_xxl'], 'bold'),
            text_color=self.theme['text_primary'],
            anchor="w",
        )
        header.grid(row=0, column=0, padx=32, pady=(32, 16), sticky="ew")

        log_container = ctk.CTkFrame(
            page,
            corner_radius=ModernTheme.RADIUS['xl'],
            fg_color=self.theme['bg_secondary'],
            border_width=1,
            border_color=self.theme['border_primary'],
        )
        log_container.grid(row=1, column=0, padx=32, pady=(0, 32), sticky="nsew")
        # 🔥 Правильные weights для адаптивного layout
        log_container.grid_columnconfigure(0, weight=1)
        log_container.grid_rowconfigure(0, weight=0)  # Clear button - фиксированная высота
        log_container.grid_rowconfigure(1, weight=1)  # Log textbox - растягивается

        # Кнопка очистки
        clear_btn = ctk.CTkButton(
            log_container,
            text="🗑️ Clear Logs",
            command=self.clear_logs,
            height=40,
            corner_radius=ModernTheme.RADIUS['lg'],
            fg_color=self.theme['accent_error'],
            hover_color=self.theme['bg_hover'],
        )
        clear_btn.grid(row=0, column=0, padx=24, pady=24, sticky="e")

        self.all_logs = ctk.CTkTextbox(
            log_container,
            corner_radius=ModernTheme.RADIUS['lg'],
            fg_color=self.theme['bg_tertiary'],
            border_width=0,
            text_color=self.theme['text_primary'],
            font=('Consolas', 11),
            wrap="word",
        )
        self.all_logs.grid(row=1, column=0, padx=24, pady=(0, 24), sticky="nsew")

        return page

    def create_settings_page(self, parent):
        """Страница Settings с collapsible секциями"""
        page = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            corner_radius=0,
        )
        page.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            page,
            text="⚙️ Settings",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_xxl'], 'bold'),
            text_color=self.theme['text_primary'],
            anchor="w",
        )
        header.grid(row=0, column=0, padx=32, pady=(32, 16), sticky="ew")

        # === API Settings ===
        api_section = CollapsibleFrame(page, title="🔌 Octobrowser API")
        api_section.grid(row=1, column=0, padx=32, pady=8, sticky="ew")

        ctk.CTkLabel(
            api_section.content_frame,
            text="API Token:",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_sm']),
            text_color=self.theme['text_secondary'],
        ).pack(anchor="w", padx=16, pady=(16, 4))

        self.api_token_entry = ctk.CTkEntry(
            api_section.content_frame,
            placeholder_text="Enter your Octobrowser API token",
            height=44,
            corner_radius=ModernTheme.RADIUS['lg'],
            border_width=1,
        )
        self.api_token_entry.pack(fill="x", padx=16, pady=(0, 8))

        connect_btn = ctk.CTkButton(
            api_section.content_frame,
            text="🔗 Connect API",
            command=self.connect_api,
            height=44,
            corner_radius=ModernTheme.RADIUS['lg'],
            fg_color=self.theme['accent_success'],
        )
        connect_btn.pack(fill="x", padx=16, pady=(8, 16))

        # === SMS Settings ===
        sms_section = CollapsibleFrame(page, title="📱 SMS Provider", collapsed=True)
        sms_section.grid(row=2, column=0, padx=32, pady=8, sticky="ew")

        ctk.CTkLabel(
            sms_section.content_frame,
            text="Provider:",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_sm']),
            text_color=self.theme['text_secondary'],
        ).pack(anchor="w", padx=16, pady=(16, 4))

        self.sms_provider_var = tk.StringVar(value="daisysms")
        sms_provider = ctk.CTkSegmentedButton(
            sms_section.content_frame,
            values=["daisysms", "smsactivate", "5sim"],
            variable=self.sms_provider_var,
            corner_radius=ModernTheme.RADIUS['lg'],
        )
        sms_provider.pack(fill="x", padx=16, pady=(0, 12))

        ctk.CTkLabel(
            sms_section.content_frame,
            text="API Key:",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_sm']),
            text_color=self.theme['text_secondary'],
        ).pack(anchor="w", padx=16, pady=(0, 4))

        self.sms_api_key_entry = ctk.CTkEntry(
            sms_section.content_frame,
            placeholder_text="Enter SMS provider API key",
            height=44,
            corner_radius=ModernTheme.RADIUS['lg'],
        )
        self.sms_api_key_entry.pack(fill="x", padx=16, pady=(0, 16))

        # === Proxy Settings ===
        proxy_section = CollapsibleFrame(page, title="🌐 Proxy", collapsed=True)
        proxy_section.grid(row=3, column=0, padx=32, pady=8, sticky="ew")

        self.use_proxy_var = tk.BooleanVar(value=False)
        proxy_toggle = ctk.CTkSwitch(
            proxy_section.content_frame,
            text="Enable Proxy",
            variable=self.use_proxy_var,
            command=self.toggle_proxy,
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_md']),
        )
        proxy_toggle.pack(anchor="w", padx=16, pady=16)

        self.proxy_frame = ctk.CTkFrame(proxy_section.content_frame, fg_color="transparent")
        
        # Proxy Type
        ctk.CTkLabel(
            self.proxy_frame,
            text="Type:",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_sm']),
            text_color=self.theme['text_secondary'],
        ).pack(anchor="w", padx=16, pady=(0, 4))

        self.proxy_type_var = tk.StringVar(value="http")
        proxy_type = ctk.CTkSegmentedButton(
            self.proxy_frame,
            values=["http", "https", "socks5"],
            variable=self.proxy_type_var,
        )
        proxy_type.pack(fill="x", padx=16, pady=(0, 12))

        # Host
        ctk.CTkLabel(
            self.proxy_frame,
            text="Host:",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_sm']),
            text_color=self.theme['text_secondary'],
        ).pack(anchor="w", padx=16, pady=(0, 4))

        self.proxy_host_entry = ctk.CTkEntry(
            self.proxy_frame,
            placeholder_text="proxy.example.com",
            height=40,
        )
        self.proxy_host_entry.pack(fill="x", padx=16, pady=(0, 12))

        # Port
        ctk.CTkLabel(
            self.proxy_frame,
            text="Port:",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_sm']),
            text_color=self.theme['text_secondary'],
        ).pack(anchor="w", padx=16, pady=(0, 4))

        self.proxy_port_entry = ctk.CTkEntry(
            self.proxy_frame,
            placeholder_text="8080",
            height=40,
        )
        self.proxy_port_entry.pack(fill="x", padx=16, pady=(0, 16))

        # === CSV Data ===
        csv_section = CollapsibleFrame(page, title="📊 CSV Data", collapsed=True)
        csv_section.grid(row=4, column=0, padx=32, pady=8, sticky="ew")

        csv_btn = ctk.CTkButton(
            csv_section.content_frame,
            text="📂 Load CSV File",
            command=self.load_csv,
            height=44,
            corner_radius=ModernTheme.RADIUS['lg'],
        )
        csv_btn.pack(fill="x", padx=16, pady=16)

        self.csv_path_entry = ctk.CTkEntry(
            csv_section.content_frame,
            placeholder_text="No CSV loaded",
            height=40,
            state="disabled",
        )
        self.csv_path_entry.pack(fill="x", padx=16, pady=(0, 16))

        # === Save Button ===
        save_btn = ctk.CTkButton(
            page,
            text="💾 Save All Settings",
            command=self.save_all_settings,
            height=56,
            corner_radius=ModernTheme.RADIUS['xl'],
            fg_color=self.theme['accent_primary'],
            hover_color=self.theme['bg_hover'],
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_lg'], 'bold'),
        )
        save_btn.grid(row=5, column=0, padx=32, pady=32, sticky="ew")

        return page

    # ========================================================================
    # НАВИГАЦИЯ
    # ========================================================================

    def switch_page(self, page_id: str):
        """Переключить активную страницу"""
        # Скрыть все страницы
        for pid, page in self.pages.items():
            page.grid_remove()

        # Показать выбранную
        if page_id in self.pages:
            self.pages[page_id].grid(row=0, column=0, sticky="nsew")
            self.current_page = page_id

        # Обновить кнопки навигации
        for pid, btn in self.nav_buttons.items():
            if pid == page_id:
                btn.configure(
                    fg_color=self.theme['accent_primary'],
                    text_color=self.theme['text_on_accent'],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self.theme['text_secondary'],
                )

    def toggle_theme(self, value):
        """Переключить тему Dark/Light"""
        if "Dark" in value:
            ctk.set_appearance_mode("dark")
            self.current_theme = 'dark'
            self.theme = ModernTheme.DARK
            self.toast.info("Темная тема активирована 🌙")
        else:
            ctk.set_appearance_mode("light")
            self.current_theme = 'light'
            self.theme = ModernTheme.LIGHT
            self.toast.info("Светлая тема активирована ☀️")

        # Обновить все виджеты (упрощенно, в реальности нужна полная перерисовка)

    def toggle_proxy(self):
        """Показать/скрыть настройки прокси"""
        if self.use_proxy_var.get():
            self.proxy_frame.pack(fill="x", padx=0, pady=(0, 16))
        else:
            self.proxy_frame.pack_forget()

    # ========================================================================
    # ИМПОРТ КОДА
    # ========================================================================

    def import_from_file(self):
        """Импорт кода из .py файла"""
        filepath = filedialog.askopenfilename(
            title="Select Playwright Python file",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )

        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    code = f.read()

                self.process_imported_code(code)
                self.toast.success(f"Файл импортирован: {Path(filepath).name}")
            except Exception as e:
                self.toast.error(f"Ошибка чтения файла: {e}")

    def import_from_clipboard(self):
        """Импорт кода из буфера обмена"""
        try:
            code = self.clipboard_get()
            if code.strip():
                self.process_imported_code(code)
                self.toast.success("Код импортирован из буфера обмена")
            else:
                self.toast.warning("Буфер обмена пуст")
        except Exception as e:
            self.toast.error(f"Ошибка чтения буфера: {e}")

    def process_imported_code(self, code: str):
        """Обработка импортированного кода"""
        try:
            # Определить тип (Selenium IDE .side или Playwright .py)
            if code.strip().startswith('{'):
                # Это JSON от Selenium IDE
                result = self.side_parser.parse_side_json(code)
            else:
                # Это Playwright Python код
                result = self.playwright_parser.parse_playwright_code(code)

            self.imported_data = result

            # Показать в редакторе
            self.code_editor.delete("1.0", "end")
            self.code_editor.insert("1.0", result.get('converted_code', code))

            # Скрыть drop zone label
            if hasattr(self, 'drop_zone_label'):
                self.drop_zone_label.place_forget()

            self.toast.success(f"Найдено действий: {len(result.get('actions', []))}")
            self.append_log(f"[INFO] Импортирован код с {len(result.get('actions', []))} действиями")

        except Exception as e:
            self.toast.error(f"Ошибка парсинга: {e}")
            self.append_log(f"[ERROR] Ошибка импорта: {e}")

    # ========================================================================
    # ЗАПУСК СКРИПТА
    # ========================================================================

    def start_script(self):
        """Запуск сгенерированного скрипта"""
        if not self.imported_data:
            self.toast.warning("Сначала импортируйте код!")
            return

        try:
            # Проверить что код есть
            code = self.code_editor.get("1.0", "end-1c").strip()
            if not code:
                self.toast.error("Редактор пуст!")
                return

            # Сохранить во временный файл
            output_dir = Path(self.config['script_settings']['output_directory'])
            output_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            script_path = output_dir / f"auto2tesst_{timestamp}.py"

            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(code)

            self.append_log(f"[INFO] Скрипт сохранен: {script_path}")

            # Запуск в отдельном потоке
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.progress_label.configure(text="Running...")
            self.progress_bar.set(0.5)

            def run_thread():
                try:
                    self.runner.run_script(str(script_path))
                    self.after(0, lambda: self.toast.success("Скрипт завершен успешно"))
                except Exception as e:
                    self.after(0, lambda: self.toast.error(f"Ошибка выполнения: {e}"))
                finally:
                    self.after(0, self.script_finished)

            thread = threading.Thread(target=run_thread, daemon=True)
            thread.start()

            self.toast.info("Скрипт запущен ▶️")

        except Exception as e:
            self.toast.error(f"Ошибка запуска: {e}")
            self.append_log(f"[ERROR] {e}")

    def stop_script(self):
        """Остановка выполнения скрипта"""
        try:
            self.runner.stop()
            self.toast.warning("Скрипт остановлен ⏹️")
            self.script_finished()
        except Exception as e:
            self.toast.error(f"Ошибка остановки: {e}")

    def script_finished(self):
        """Обработка завершения скрипта"""
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.progress_label.configure(text="Ready to run")
        self.progress_bar.set(0)

    # ========================================================================
    # ЛОГИ
    # ========================================================================

    def append_log(self, message: str):
        """Добавить сообщение в лог с цветовой подсветкой"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}\n"

        # Добавить в run log
        if hasattr(self, 'run_log'):
            self.run_log.insert("end", formatted)
            self.run_log.see("end")  # Автоскролл

        # Добавить в all logs
        if hasattr(self, 'all_logs'):
            self.all_logs.insert("end", formatted)
            self.all_logs.see("end")

        # TODO: Цветовая подсветка через tags (требует доп. настройки)
        # Например: self.run_log.tag_config("INFO", foreground=self.theme['log_info'])

    def clear_logs(self):
        """Очистить все логи"""
        if hasattr(self, 'run_log'):
            self.run_log.delete("1.0", "end")
        if hasattr(self, 'all_logs'):
            self.all_logs.delete("1.0", "end")
        self.toast.info("Логи очищены")

    # ========================================================================
    # НАСТРОЙКИ
    # ========================================================================

    def connect_api(self):
        """Подключение к Octobrowser API"""
        token = self.api_token_entry.get().strip()
        if not token:
            self.toast.warning("Введите API токен")
            return

        try:
            self.config['octobrowser']['api_token'] = token
            self.api = OctobrowserAPI(
                token,
                self.config['octobrowser']['api_base_url']
            )

            # Проверка подключения
            result = self.api.get_profiles(page=0, page_len=1)

            if 'error' in result:
                self.toast.error(f"Ошибка API: {result['error']}")
                return

            self.toast.success("API подключен успешно ✅")
            self.append_log("[INFO] Octobrowser API подключен")

        except Exception as e:
            self.toast.error(f"Ошибка подключения: {e}")
            self.append_log(f"[ERROR] API: {e}")

    def load_csv(self):
        """Загрузка CSV файла"""
        filepath = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filepath:
            try:
                # TODO: Парсинг CSV
                self.config['ui_settings']['last_csv_path'] = filepath
                self.csv_path_entry.configure(state="normal")
                self.csv_path_entry.delete(0, "end")
                self.csv_path_entry.insert(0, filepath)
                self.csv_path_entry.configure(state="disabled")
                self.toast.success(f"CSV загружен: {Path(filepath).name}")
            except Exception as e:
                self.toast.error(f"Ошибка загрузки CSV: {e}")

    def save_all_settings(self):
        """Сохранить все настройки в config.json"""
        try:
            # SMS
            self.config.setdefault('sms', {})
            self.config['sms']['api_key'] = self.sms_api_key_entry.get().strip()
            self.config['sms']['provider'] = self.sms_provider_var.get()

            # Proxy
            self.config.setdefault('proxy', {})
            self.config['proxy']['enabled'] = self.use_proxy_var.get()
            self.config['proxy']['type'] = self.proxy_type_var.get()
            self.config['proxy']['host'] = self.proxy_host_entry.get().strip()
            self.config['proxy']['port'] = self.proxy_port_entry.get().strip()

            # API
            self.config.setdefault('octobrowser', {})
            self.config['octobrowser']['api_token'] = self.api_token_entry.get().strip()

            self.save_config()
            self.append_log("[INFO] Настройки сохранены")

        except Exception as e:
            self.toast.error(f"Ошибка сохранения: {e}")

    # ========================================================================
    # DRAG & DROP
    # ========================================================================

    def setup_drag_drop(self):
        """Настройка drag & drop для импорта файлов"""
        try:
            # Для drag & drop нужен TkinterDnD.Tk вместо ctk.CTk
            # Упрощенная версия: только через кнопки
            # TODO: Полная интеграция с tkinterdnd2
            pass
        except Exception as e:
            print(f"Drag & drop not available: {e}")

    # ========================================================================
    # ГОРЯЧИЕ КЛАВИШИ
    # ========================================================================

    def setup_hotkeys(self):
        """Настройка горячих клавиш"""
        # Ctrl+I - Import
        self.bind("<Control-i>", lambda e: self.import_from_file())
        self.bind("<Control-I>", lambda e: self.import_from_file())

        # Ctrl+R - Run
        self.bind("<Control-r>", lambda e: self.start_script())
        self.bind("<Control-R>", lambda e: self.start_script())

        # Esc - Stop
        self.bind("<Escape>", lambda e: self.stop_script() if self.stop_btn.cget("state") == "normal" else None)

        # Ctrl+S - Save settings
        self.bind("<Control-s>", lambda e: self.save_all_settings())
        self.bind("<Control-S>", lambda e: self.save_all_settings())

        # Ctrl+L - Clear logs
        self.bind("<Control-l>", lambda e: self.clear_logs())
        self.bind("<Control-L>", lambda e: self.clear_logs())


# ============================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================================

def main():
    """Запуск приложения"""
    app = ModernApp()
    app.mainloop()


if __name__ == "__main__":
    main()
