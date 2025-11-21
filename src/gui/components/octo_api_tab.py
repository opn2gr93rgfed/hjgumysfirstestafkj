"""
🐙 Octo API Tab - Полные настройки Octobrowser API

Функции:
- API Token configuration
- Default Tags управление
- Default Plugins (upload .zip or folder)
- Fingerprint overrides (OS, WebRTC, Canvas, Fonts, etc.)
- Notes field
- Profile templates
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from typing import Dict, List, Optional
from pathlib import Path
import json
import requests


class OctoAPITab(ctk.CTkScrollableFrame):
    """
    Вкладка настроек Octobrowser API
    """

    def __init__(self, parent, theme: Dict, config: Dict, toast_manager=None, save_callback=None):
        super().__init__(parent, fg_color="transparent", corner_radius=0)

        self.theme = theme
        self.config = config
        self.toast = toast_manager
        self.save_callback = save_callback  # 🔥 Callback для централизованного сохранения

        print(f"[OCTO_TAB] __init__ вызван")
        print(f"[OCTO_TAB] config id: {id(config)}")
        token = config.get('octobrowser', {}).get('api_token', '')
        print(f"[OCTO_TAB] Токен при инициализации: {token[:10]}..." if token else "[OCTO_TAB] Токен при инициализации пуст")

        self.grid_columnconfigure(0, weight=1)

        # Переменная для хранения UUID тестового профиля
        self.test_profile_uuid = None

        self.create_widgets()

        # 🔥 ЗАГРУЗИТЬ СОХРАНЕННЫЕ НАСТРОЙКИ
        self.load_saved_settings()

    def create_widgets(self):
        """Создать виджеты"""
        # === HEADER ===
        header = ctk.CTkLabel(
            self,
            text="🐙 Octobrowser API Settings",
            font=('Segoe UI', 24, 'bold'),
            text_color=self.theme['text_primary'],
            anchor="w"
        )
        header.grid(row=0, column=0, padx=32, pady=(32, 16), sticky="ew")

        # === API TOKEN SECTION ===
        token_section = self.create_collapsible_section(
            "🔐 API Token Configuration",
            row=1
        )

        ctk.CTkLabel(
            token_section,
            text="Access Token:",
            font=('Segoe UI', 11),
            text_color=self.theme['text_secondary'],
            anchor="w"
        ).pack(anchor="w", padx=16, pady=(16, 4))

        self.token_entry = ctk.CTkEntry(
            token_section,
            placeholder_text="Enter your Octobrowser API token",
            height=44,
            font=('Consolas', 11),
            fg_color=self.theme['bg_tertiary'],
            border_width=1
        )
        self.token_entry.pack(fill="x", padx=16, pady=(0, 8))

        # Load saved token
        saved_token = self.config.get('octobrowser', {}).get('api_token', '')
        if saved_token:
            self.token_entry.insert(0, saved_token)

        ctk.CTkLabel(
            token_section,
            text="Base URL:",
            font=('Segoe UI', 11),
            text_color=self.theme['text_secondary'],
            anchor="w"
        ).pack(anchor="w", padx=16, pady=(8, 4))

        self.base_url_entry = ctk.CTkEntry(
            token_section,
            height=44,
            font=('Consolas', 11),
            fg_color=self.theme['bg_tertiary']
        )
        # 🔥 ПРАВИЛЬНЫЙ Base URL с /automation согласно официальной документации
        # https://documenter.getpostman.com/view/1801428/UVC6i6eA
        # Загружаем сохраненный URL или используем default
        saved_base_url = self.config.get('octobrowser', {}).get('api_base_url', '')
        if not saved_base_url:
            saved_base_url = "https://app.octobrowser.net/api/v2/automation"
        self.base_url_entry.insert(0, saved_base_url)
        self.base_url_entry.pack(fill="x", padx=16, pady=(0, 8))

        test_btn = ctk.CTkButton(
            token_section,
            text="🔍 Test Connection",
            command=self.test_connection,
            height=44,
            fg_color=self.theme['accent_info'],
            hover_color=self.theme['bg_hover'],
            font=('Segoe UI', 11, 'bold')
        )
        test_btn.pack(fill="x", padx=16, pady=(8, 16))

        # === TAGS SECTION ===
        tags_section = self.create_collapsible_section(
            "🏷️ Default Tags",
            row=2
        )

        ctk.CTkLabel(
            tags_section,
            text="Tags (comma-separated):",
            font=('Segoe UI', 11),
            text_color=self.theme['text_secondary'],
            anchor="w"
        ).pack(anchor="w", padx=16, pady=(16, 4))

        self.tags_entry = ctk.CTkEntry(
            tags_section,
            placeholder_text="leadgen, us, automation",
            height=44,
            font=('Consolas', 11),
            fg_color=self.theme['bg_tertiary']
        )
        self.tags_entry.pack(fill="x", padx=16, pady=(0, 16))

        # === PLUGINS SECTION ===
        plugins_section = self.create_collapsible_section(
            "🔌 Default Plugins",
            row=3
        )

        self.plugins_listbox = ctk.CTkTextbox(
            plugins_section,
            height=100,
            font=('Consolas', 10),
            fg_color=self.theme['bg_tertiary']
        )
        self.plugins_listbox.pack(fill="x", padx=16, pady=(16, 8))

        plugins_btn_frame = ctk.CTkFrame(plugins_section, fg_color="transparent")
        plugins_btn_frame.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkButton(
            plugins_btn_frame,
            text="📂 Add Plugin (.zip)",
            command=self.add_plugin_zip,
            height=36,
            fg_color=self.theme['accent_secondary'],
            font=('Segoe UI', 10)
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            plugins_btn_frame,
            text="📁 Add Folder",
            command=self.add_plugin_folder,
            height=36,
            fg_color=self.theme['accent_secondary'],
            font=('Segoe UI', 10)
        ).pack(side="left")

        # === FINGERPRINT OVERRIDES ===
        fp_section = self.create_collapsible_section(
            "🔍 Fingerprint Overrides",
            row=4
        )

        # OS Selection
        os_frame = ctk.CTkFrame(fp_section, fg_color="transparent")
        os_frame.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(
            os_frame,
            text="Operating System:",
            font=('Segoe UI', 11),
            text_color=self.theme['text_secondary'],
            width=150,
            anchor="w"
        ).pack(side="left", padx=(0, 8))

        self.os_var = tk.StringVar(value="random")
        os_segment = ctk.CTkSegmentedButton(
            os_frame,
            values=["Random", "Windows", "macOS", "Linux"],
            variable=self.os_var,
            fg_color=self.theme['bg_tertiary'],
            selected_color=self.theme['accent_primary'],
            font=('Segoe UI', 10)
        )
        os_segment.pack(side="left", fill="x", expand=True)
        os_segment.set("Random")

        # WebRTC Mode
        webrtc_frame = ctk.CTkFrame(fp_section, fg_color="transparent")
        webrtc_frame.pack(fill="x", padx=16, pady=8)

        ctk.CTkLabel(
            webrtc_frame,
            text="WebRTC Mode:",
            font=('Segoe UI', 11),
            text_color=self.theme['text_secondary'],
            width=150,
            anchor="w"
        ).pack(side="left", padx=(0, 8))

        self.webrtc_var = tk.StringVar(value="altered")
        webrtc_segment = ctk.CTkSegmentedButton(
            webrtc_frame,
            values=["Disabled", "Real", "Altered"],
            variable=self.webrtc_var,
            fg_color=self.theme['bg_tertiary'],
            selected_color=self.theme['accent_primary'],
            font=('Segoe UI', 10)
        )
        webrtc_segment.pack(side="left", fill="x", expand=True)
        webrtc_segment.set("Altered")

        # Canvas Protection
        self.canvas_var = tk.BooleanVar(value=True)
        canvas_switch = ctk.CTkSwitch(
            fp_section,
            text="Canvas Protection",
            variable=self.canvas_var,
            font=('Segoe UI', 11)
        )
        canvas_switch.pack(anchor="w", padx=16, pady=8)

        # WebGL Protection
        self.webgl_var = tk.BooleanVar(value=True)
        webgl_switch = ctk.CTkSwitch(
            fp_section,
            text="WebGL Protection",
            variable=self.webgl_var,
            font=('Segoe UI', 11)
        )
        webgl_switch.pack(anchor="w", padx=16, pady=8)

        # Fonts Protection
        self.fonts_var = tk.BooleanVar(value=True)
        fonts_switch = ctk.CTkSwitch(
            fp_section,
            text="Fonts Protection",
            variable=self.fonts_var,
            font=('Segoe UI', 11)
        )
        fonts_switch.pack(anchor="w", padx=16, pady=(8, 16))

        # === GEOLOCATION ===
        geo_section = self.create_collapsible_section(
            "🌍 Geolocation Settings",
            row=5
        )

        self.geo_enabled_var = tk.BooleanVar(value=False)
        geo_switch = ctk.CTkSwitch(
            geo_section,
            text="Enable Custom Geolocation",
            variable=self.geo_enabled_var,
            command=self.toggle_geo,
            font=('Segoe UI', 11)
        )
        geo_switch.pack(anchor="w", padx=16, pady=16)

        self.geo_frame = ctk.CTkFrame(geo_section, fg_color="transparent")

        geo_grid = ctk.CTkFrame(self.geo_frame, fg_color="transparent")
        geo_grid.pack(fill="x", padx=16, pady=(0, 16))
        geo_grid.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            geo_grid,
            text="Latitude:",
            font=('Segoe UI', 10),
            text_color=self.theme['text_secondary']
        ).grid(row=0, column=0, sticky="w", pady=4)

        self.lat_entry = ctk.CTkEntry(
            geo_grid,
            placeholder_text="40.7128",
            height=36,
            font=('Consolas', 10)
        )
        self.lat_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(
            geo_grid,
            text="Longitude:",
            font=('Segoe UI', 10),
            text_color=self.theme['text_secondary']
        ).grid(row=0, column=1, sticky="w", pady=4)

        self.lon_entry = ctk.CTkEntry(
            geo_grid,
            placeholder_text="-74.0060",
            height=36,
            font=('Consolas', 10)
        )
        self.lon_entry.grid(row=1, column=1, sticky="ew")

        # === NOTES ===
        notes_section = self.create_collapsible_section(
            "📝 Profile Notes",
            row=6
        )

        self.notes_textbox = ctk.CTkTextbox(
            notes_section,
            height=120,
            font=('Consolas', 10),
            fg_color=self.theme['bg_tertiary']
        )
        self.notes_textbox.pack(fill="both", padx=16, pady=16)

        # === ADVANCED SETTINGS ===
        advanced_section = self.create_collapsible_section(
            "⚙️ Advanced Settings",
            row=7
        )

        # OTP Handler Enable/Disable
        self.otp_enabled_var = tk.BooleanVar(value=False)
        otp_switch = ctk.CTkSwitch(
            advanced_section,
            text="Enable OTP/SMS Handler (for verification codes)",
            variable=self.otp_enabled_var,
            font=('Segoe UI', 11)
        )
        otp_switch.pack(anchor="w", padx=16, pady=16)

        ctk.CTkLabel(
            advanced_section,
            text="⚠️ Note: Disable this if regular input fields (like ZIP code) are detected as OTP fields",
            font=('Segoe UI', 9),
            text_color=self.theme.get('text_muted', '#888888'),
            anchor="w",
            wraplength=600
        ).pack(anchor="w", padx=16, pady=(0, 16))

        # === TEST SECTION ===
        test_section = self.create_collapsible_section(
            "🧪 Тестирование API (отладка)",
            row=8
        )

        # Информация о тестировании
        ctk.CTkLabel(
            test_section,
            text="Используйте эти функции для проверки работы Octobrowser API:",
            font=('Segoe UI', 11),
            text_color=self.theme['text_secondary'],
            anchor="w",
            wraplength=700
        ).pack(anchor="w", padx=16, pady=(16, 4))

        # Кнопки тестирования
        test_buttons_frame = ctk.CTkFrame(test_section, fg_color="transparent")
        test_buttons_frame.pack(fill="x", padx=16, pady=(8, 16))
        test_buttons_frame.grid_columnconfigure(0, weight=1)
        test_buttons_frame.grid_columnconfigure(1, weight=1)

        # Test Create Profile button
        ctk.CTkButton(
            test_buttons_frame,
            text="1️⃣ Создать тестовый профиль",
            command=self.test_create_profile,
            height=48,
            fg_color=self.theme['accent_info'],
            hover_color=self.theme['bg_hover'],
            font=('Segoe UI', 12, 'bold')
        ).grid(row=0, column=0, padx=(0, 6), pady=4, sticky="ew")

        # Test Start Profile button
        ctk.CTkButton(
            test_buttons_frame,
            text="2️⃣ Запустить тестовый профиль",
            command=self.test_start_profile,
            height=48,
            fg_color=self.theme['accent_success'],
            hover_color=self.theme['bg_hover'],
            font=('Segoe UI', 12, 'bold')
        ).grid(row=0, column=1, padx=(6, 0), pady=4, sticky="ew")

        # Статус тестового профиля
        self.test_profile_status = ctk.CTkLabel(
            test_section,
            text="📋 Статус: Профиль не создан",
            font=('Consolas', 10),
            text_color=self.theme['text_secondary'],
            anchor="w"
        )
        self.test_profile_status.pack(anchor="w", padx=16, pady=(0, 16))

        # === BUTTONS FRAME ===
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.grid(row=9, column=0, padx=32, pady=32, sticky="ew")
        buttons_frame.grid_columnconfigure(0, weight=1)

        # Save button
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Сохранить настройки API",
            command=self.save_settings,
            height=56,
            fg_color=self.theme['accent_primary'],
            hover_color=self.theme['bg_hover'],
            font=('Segoe UI', 14, 'bold')
        )
        save_btn.grid(row=0, column=0, sticky="ew")

    def create_collapsible_section(self, title: str, row: int) -> ctk.CTkFrame:
        """Создать сворачиваемую секцию"""
        from .collapsible_frame import CollapsibleFrame

        section = CollapsibleFrame(self, title=title)
        section.grid(row=row, column=0, padx=32, pady=8, sticky="ew")
        return section.content_frame

    def toggle_geo(self):
        """Переключить геолокацию"""
        if self.geo_enabled_var.get():
            self.geo_frame.pack(fill="x", padx=0, pady=0)
        else:
            self.geo_frame.pack_forget()

    def add_plugin_zip(self):
        """Добавить плагин из .zip"""
        filepath = filedialog.askopenfilename(
            title="Select Plugin ZIP",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )

        if filepath:
            current_text = self.plugins_listbox.get("1.0", "end-1c")
            if current_text.strip():
                self.plugins_listbox.insert("end", "\n")
            self.plugins_listbox.insert("end", filepath)

            if self.toast:
                self.toast.success(f"Плагин добавлен: {Path(filepath).name}")

    def add_plugin_folder(self):
        """Добавить плагин из папки"""
        folderpath = filedialog.askdirectory(title="Select Plugin Folder")

        if folderpath:
            current_text = self.plugins_listbox.get("1.0", "end-1c")
            if current_text.strip():
                self.plugins_listbox.insert("end", "\n")
            self.plugins_listbox.insert("end", folderpath)

            if self.toast:
                self.toast.success(f"Папка плагина добавлена: {Path(folderpath).name}")

    def test_connection(self):
        """Тестировать подключение к API"""
        import requests

        print("[DEBUG] test_connection() вызван")  # DEBUG
        print(f"[DEBUG] self.toast = {self.toast}")  # DEBUG

        token = self.token_entry.get().strip()
        base_url = self.base_url_entry.get().strip()

        print(f"[DEBUG] token = {token[:10]}..." if token else "[DEBUG] token пуст")  # DEBUG
        print(f"[DEBUG] base_url = {base_url}")  # DEBUG

        if not token:
            print("[DEBUG] Токен пуст, показываю warning")  # DEBUG
            if self.toast:
                self.toast.warning("Введите API Token")
            return

        print("[DEBUG] Показываю info toast")  # DEBUG
        if self.toast:
            self.toast.info("Тестирую подключение...")

        print("[DEBUG] Начинаю запрос к API")  # DEBUG
        try:
            # Прямой запрос с правильным заголовком X-Octo-Api-Token
            # Официальная документация: https://docs.octobrowser.net/
            # Для теста подключения просто запрашиваем список профилей без параметров
            response = requests.get(
                f"{base_url}/profiles",
                headers={"X-Octo-Api-Token": token},
                timeout=10
            )

            print(f"[DEBUG] Получен ответ: status_code={response.status_code}")  # DEBUG

            # Вывод полного ответа для отладки 400 ошибок
            if response.status_code == 400:
                print(f"[DEBUG] Response body: {response.text}")  # DEBUG

            if response.status_code == 200:
                print("[DEBUG] Успех! Показываю success toast")  # DEBUG
                if self.toast:
                    self.toast.success("✅ Octo API подключён успешно!")
                # Автосохранение после успешного подключения
                self.save_settings()
            elif response.status_code == 401:
                print("[DEBUG] 401 Unauthorized")  # DEBUG
                if self.toast:
                    self.toast.error("❌ Неверный токен (401 Unauthorized)")
            elif response.status_code == 403:
                print("[DEBUG] 403 Forbidden")  # DEBUG
                if self.toast:
                    self.toast.error("❌ Доступ запрещён (403 Forbidden)")
            else:
                print(f"[DEBUG] Другой код: {response.status_code}")  # DEBUG
                if self.toast:
                    self.toast.error(f"Ошибка {response.status_code}: {response.text[:100]}")

        except requests.exceptions.ConnectionError as e:
            print(f"[DEBUG] ConnectionError: {e}")  # DEBUG
            if self.toast:
                self.toast.error("❌ Нет соединения с Octo Browser")
        except requests.exceptions.Timeout as e:
            print(f"[DEBUG] Timeout: {e}")  # DEBUG
            if self.toast:
                self.toast.error("❌ Превышено время ожидания")
        except Exception as e:
            print(f"[DEBUG] Exception: {e}")  # DEBUG
            import traceback
            traceback.print_exc()  # DEBUG
            if self.toast:
                self.toast.error(f"Ошибка: {str(e)}")

    def test_create_profile(self):
        """🧪 Тестовое создание профиля Octobrowser"""
        import time

        print("[TEST_PROFILE] === НАЧАЛО ТЕСТА СОЗДАНИЯ ПРОФИЛЯ ===")

        token = self.token_entry.get().strip()
        base_url = self.base_url_entry.get().strip()

        if not token:
            if self.toast:
                self.toast.warning("⚠️ Введите API Token")
            return

        if self.toast:
            self.toast.info("🧪 Создаю тестовый профиль...")

        # Получить настройки профиля
        profile_config = self.get_profile_config()

        # Подготовить данные профиля
        profile_data = {
            "title": f"TestProfile_{int(time.time())}",
            "fingerprint": profile_config.get('fingerprint', {"os": "win"})
        }

        # Добавить теги если есть
        if profile_config.get('tags'):
            profile_data["tags"] = profile_config['tags']

        # Добавить заметки если есть
        if profile_config.get('notes'):
            profile_data["notes"] = profile_config['notes']

        # Добавить geolocation если включено
        if profile_config.get('geolocation'):
            profile_data["geolocation"] = profile_config['geolocation']

        # 🔥 ДОБАВИТЬ ПРОКСИ ЕСЛИ ВКЛЮЧЕНО
        if self.config.get('proxy', {}).get('enabled', False):
            proxy_config = self.config.get('proxy', {})
            profile_data["proxy"] = {
                "type": proxy_config.get('type', 'http'),
                "host": proxy_config.get('host', ''),
                "port": proxy_config.get('port', ''),
                "login": proxy_config.get('login', ''),
                "password": proxy_config.get('password', '')
            }
            print(f"[TEST_PROFILE] 🌐 Добавлен прокси: {proxy_config.get('type')}://{proxy_config.get('host')}:{proxy_config.get('port')}")

        try:
            print(f"[TEST_PROFILE] Отправка запроса на создание профиля...")
            print(f"[TEST_PROFILE] URL: {base_url}/profiles")
            print(f"[TEST_PROFILE] Данные: {profile_data}")

            response = requests.post(
                f"{base_url}/profiles",
                headers={"X-Octo-Api-Token": token},
                json=profile_data,
                timeout=10
            )

            print(f"[TEST_PROFILE] Ответ: {response.status_code}")
            print(f"[TEST_PROFILE] Body: {response.text[:500]}")

            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                if result.get('success') and 'data' in result:
                    profile_uuid = result['data']['uuid']

                    # Сохранить UUID для дальнейшего тестирования
                    self.test_profile_uuid = profile_uuid

                    # Обновить статус
                    if hasattr(self, 'test_profile_status'):
                        self.test_profile_status.configure(
                            text=f"📋 Профиль создан: {profile_uuid}",
                            text_color=self.theme['accent_success']
                        )

                    print(f"[TEST_PROFILE] ✅ Профиль создан: {profile_uuid}")
                    if self.toast:
                        self.toast.success(f"✅ Профиль создан!\nUUID: {profile_uuid[:8]}...\n\nТеперь можно нажать '2️⃣ Запустить тестовый профиль'")
                else:
                    print(f"[TEST_PROFILE] ❌ Неожиданный формат ответа: {result}")
                    if self.toast:
                        self.toast.warning(f"⚠️ Профиль создан, но непонятный ответ")
            else:
                print(f"[TEST_PROFILE] ❌ Ошибка {response.status_code}: {response.text}")
                if self.toast:
                    self.toast.error(f"❌ Ошибка {response.status_code}: {response.text[:100]}")

        except Exception as e:
            print(f"[TEST_PROFILE] ❌ Exception: {e}")
            import traceback
            traceback.print_exc()
            if self.toast:
                self.toast.error(f"❌ Ошибка: {str(e)}")

    def test_start_profile(self):
        """🧪 Тестовый запуск профиля через Local API"""
        import time

        print("[TEST_START] === НАЧАЛО ТЕСТА ЗАПУСКА ПРОФИЛЯ ===")

        if not self.test_profile_uuid:
            if self.toast:
                self.toast.warning("⚠️ Сначала создайте тестовый профиль!\nНажмите '1️⃣ Создать тестовый профиль'")
            return

        if self.toast:
            self.toast.info(f"🧪 Запускаю профиль {self.test_profile_uuid[:8]}...")

        # Local API endpoint
        local_api_url = "http://localhost:58888/api"

        try:
            # ШАГ 1: Проверка доступности Local API
            print(f"[TEST_START] Проверка доступности {local_api_url}")
            try:
                response = requests.get(f"{local_api_url}/profiles", timeout=5)
                if response.status_code in [200, 404]:
                    print(f"[TEST_START] ✅ Local API доступен")
                    if self.toast:
                        self.toast.success("✅ Local API доступен (Octobrowser запущен)")
                else:
                    print(f"[TEST_START] ⚠️ Неожиданный статус: {response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"[TEST_START] ❌ Не удалось подключиться к {local_api_url}")
                if self.toast:
                    self.toast.error(f"❌ Local API недоступен!\n\nОктобраузер не запущен на localhost:58888")
                return

            # ШАГ 2: Ожидание синхронизации
            print(f"[TEST_START] Ожидание синхронизации профиля (5 секунд)...")
            if self.toast:
                self.toast.info("⏳ Ожидание синхронизации Cloud → Local...")
            time.sleep(5)

            # ШАГ 3: Запуск профиля
            max_retries = 8
            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        wait_time = 2 ** (attempt - 1) * 2  # 2s, 4s, 8s, 16s, 32s, 64s, 128s
                        print(f"[TEST_START] Ожидание синхронизации: {wait_time}s")
                        time.sleep(wait_time)

                    print(f"[TEST_START] Попытка запуска {attempt+1}/{max_retries}: {self.test_profile_uuid}")

                    # ============================================================
                    # ⚠️ КРИТИЧЕСКИ ВАЖНО: ЕДИНСТВЕННО ПРАВИЛЬНЫЙ СПОСОБ ЗАПУСКА ПРОФИЛЯ!
                    # ============================================================
                    # Метод: POST (НЕ GET!)
                    # URL: /profiles/start (НЕ /profiles/{uuid}/start!)
                    # Body: JSON с uuid и параметрами
                    #
                    # ❌ НЕПРАВИЛЬНО: GET /profiles/{uuid}/start
                    # ✅ ПРАВИЛЬНО: POST /profiles/start с body
                    #
                    # Это ПРОТЕСТИРОВАННЫЙ И РАБОТАЮЩИЙ способ!
                    # Все остальные варианты НЕ работают и вызывают 404!
                    # Используйте ТОЛЬКО этот пример во всех будущих провайдерах!
                    # ============================================================
                    response = requests.post(
                        f"{local_api_url}/profiles/start",
                        json={
                            "uuid": self.test_profile_uuid,
                            "debug_port": True,
                            "headless": False,
                            "only_local": True,
                            "timeout": 120
                        },
                        timeout=120
                    )

                    print(f"[TEST_START] Ответ: {response.status_code}")

                    if response.status_code == 200:
                        data = response.json()
                        print(f"[TEST_START] ✅ Профиль запущен!")
                        print(f"[TEST_START] CDP endpoint: {data.get('ws_endpoint', 'N/A')}")

                        # Обновить статус
                        if hasattr(self, 'test_profile_status'):
                            self.test_profile_status.configure(
                                text=f"✅ Профиль запущен: {self.test_profile_uuid}",
                                text_color=self.theme['accent_success']
                            )

                        if self.toast:
                            self.toast.success(f"✅ Профиль успешно запущен!\n\nCDP: {data.get('ws_endpoint', '')[:30]}...")

                        return  # Успех

                    elif response.status_code == 404:
                        print(f"[TEST_START] [!] Профиль еще не синхронизирован с локальным Octobrowser")
                        if attempt == max_retries - 1:
                            # Последняя попытка
                            if self.toast:
                                self.toast.error(f"❌ Профиль не синхронизировался!\n\nПрофиль создан в облаке, но не появился в локальном Octobrowser после {max_retries} попыток")
                        continue

                    else:
                        print(f"[TEST_START] ❌ Ошибка {response.status_code}: {response.text}")
                        if self.toast:
                            self.toast.error(f"❌ Ошибка {response.status_code}: {response.text[:100]}")
                        return

                except requests.exceptions.Timeout:
                    print(f"[TEST_START] ❌ Timeout при запуске профиля")
                    if attempt == max_retries - 1:
                        if self.toast:
                            self.toast.error("❌ Timeout при запуске профиля")
                    continue

                except Exception as e:
                    print(f"[TEST_START] ❌ Exception: {e}")
                    if self.toast:
                        self.toast.error(f"❌ Ошибка: {str(e)}")
                    return

            # Если все попытки исчерпаны
            if hasattr(self, 'test_profile_status'):
                self.test_profile_status.configure(
                    text=f"❌ Не удалось запустить профиль после {max_retries} попыток",
                    text_color=self.theme['accent_error']
                )

        except Exception as e:
            print(f"[TEST_START] ❌ Exception: {e}")
            import traceback
            traceback.print_exc()
            if self.toast:
                self.toast.error(f"❌ Ошибка: {str(e)}")

    def save_settings(self):
        """
        Сохранить настройки в config (в памяти)

        Файл сохраняется через централизованный метод главного окна.
        """
        print("[OCTO_TAB] === save_settings() - обновление config в памяти ===")

        # Update config в памяти
        token = self.token_entry.get().strip()
        base_url = self.base_url_entry.get().strip()

        print(f"[OCTO_TAB] Обновляю токен: {token[:10]}..." if token else "[OCTO_TAB] Токен пуст")
        print(f"[OCTO_TAB] Обновляю base_url: {base_url}")

        self.config.setdefault('octobrowser', {})
        self.config['octobrowser']['api_token'] = token
        self.config['octobrowser']['api_base_url'] = base_url

        self.config.setdefault('octo_defaults', {})
        self.config['octo_defaults']['tags'] = [
            tag.strip() for tag in self.tags_entry.get().split(',') if tag.strip()
        ]
        self.config['octo_defaults']['plugins'] = [
            plugin.strip() for plugin in self.plugins_listbox.get("1.0", "end-1c").split('\n') if plugin.strip()
        ]
        self.config['octo_defaults']['notes'] = self.notes_textbox.get("1.0", "end-1c").strip()

        # Fingerprint settings
        self.config.setdefault('fingerprint', {})
        self.config['fingerprint']['os'] = self.os_var.get().lower()
        self.config['fingerprint']['webrtc'] = self.webrtc_var.get().lower()
        self.config['fingerprint']['canvas_protection'] = self.canvas_var.get()
        self.config['fingerprint']['webgl_protection'] = self.webgl_var.get()
        self.config['fingerprint']['fonts_protection'] = self.fonts_var.get()

        # Geolocation
        self.config.setdefault('geolocation', {})
        self.config['geolocation']['enabled'] = self.geo_enabled_var.get()
        self.config['geolocation']['latitude'] = self.lat_entry.get().strip()
        self.config['geolocation']['longitude'] = self.lon_entry.get().strip()

        # OTP Handler
        self.config.setdefault('otp', {})
        self.config['otp']['enabled'] = self.otp_enabled_var.get()
        self.config['otp']['auto_detect_fields'] = self.otp_enabled_var.get()

        print(f"[OCTO_TAB] ✅ Config обновлён в памяти")
        print(f"[OCTO_TAB] OTP enabled: {self.config['otp']['enabled']}")
        print(f"[OCTO_TAB] Токен в self.config: {self.config.get('octobrowser', {}).get('api_token', '')[:10]}...")

        # 🔥 ЦЕНТРАЛИЗОВАННОЕ СОХРАНЕНИЕ через callback
        if self.save_callback:
            print(f"[OCTO_TAB] Вызываю save_callback() для записи на диск...")
            self.save_callback()
        else:
            print(f"[OCTO_TAB] ⚠️ save_callback не установлен!")
            if self.toast:
                self.toast.warning("Настройки обновлены, но не сохранены")

    def load_saved_settings(self):
        """Загрузить сохраненные настройки из config"""
        # Tags
        saved_tags = self.config.get('octo_defaults', {}).get('tags', [])
        if saved_tags:
            self.tags_entry.insert(0, ', '.join(saved_tags))

        # Plugins
        saved_plugins = self.config.get('octo_defaults', {}).get('plugins', [])
        if saved_plugins:
            self.plugins_listbox.delete("1.0", "end")
            self.plugins_listbox.insert("1.0", '\n'.join(saved_plugins))

        # Notes
        saved_notes = self.config.get('octo_defaults', {}).get('notes', '')
        if saved_notes:
            self.notes_textbox.delete("1.0", "end")
            self.notes_textbox.insert("1.0", saved_notes)

        # Fingerprint
        fingerprint = self.config.get('fingerprint', {})
        if fingerprint:
            os_value = fingerprint.get('os', 'win').capitalize()
            if os_value.lower() == 'random':
                os_value = 'Random'
            self.os_var.set(os_value)

            webrtc_value = fingerprint.get('webrtc', 'altered').capitalize()
            self.webrtc_var.set(webrtc_value)

            self.canvas_var.set(fingerprint.get('canvas_protection', True))
            self.webgl_var.set(fingerprint.get('webgl_protection', True))
            self.fonts_var.set(fingerprint.get('fonts_protection', True))

        # Geolocation
        geo = self.config.get('geolocation', {})
        if geo:
            self.geo_enabled_var.set(geo.get('enabled', False))

            lat = geo.get('latitude', '')
            if lat:
                self.lat_entry.insert(0, lat)

            lon = geo.get('longitude', '')
            if lon:
                self.lon_entry.insert(0, lon)

        # OTP Handler
        otp_config = self.config.get('otp', {})
        otp_enabled = otp_config.get('enabled', False)
        self.otp_enabled_var.set(otp_enabled)
        print(f"[OCTO_TAB] Загружен OTP enabled: {otp_enabled}")

    def get_profile_config(self) -> Dict:
        """
        Получить конфигурацию профиля для создания через API

        Returns:
            Словарь с настройками профиля
        """
        # 🔥 ИСПРАВЛЕНИЕ: Конвертация OS в правильный формат API
        # Windows → win, Mac → mac (по документации)
        os_value = self.os_var.get()
        if os_value == 'Windows':
            api_os = 'win'
        elif os_value == 'Mac':
            api_os = 'mac'
        elif os_value == 'Random':
            api_os = 'win'  # Default для random
        else:
            api_os = os_value.lower()  # Fallback

        # МИНИМАЛЬНЫЙ fingerprint (по официальной документации)
        # https://documenter.getpostman.com/view/1801428/UVC6i6eA
        config = {
            'tags': [tag.strip() for tag in self.tags_entry.get().split(',') if tag.strip()],
            'notes': self.notes_textbox.get("1.0", "end-1c").strip(),
            'fingerprint': {
                'os': api_os  # Только обязательное поле
            }
        }

        # Geolocation
        if self.geo_enabled_var.get():
            try:
                lat = float(self.lat_entry.get())
                lon = float(self.lon_entry.get())
                config['geolocation'] = {
                    'mode': 'manual',
                    'latitude': lat,
                    'longitude': lon
                }
            except:
                pass

        return config
