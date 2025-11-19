#!/usr/bin/env python3
"""
Автоматически сгенерированный скрипт автоматизации
Фреймворк: Playwright (SYNC API)
Браузер: Octobrowser (через CDP)
"""

import csv
import time
import random
import requests
from playwright.sync_api import sync_playwright, Playwright, expect
from typing import Dict, List, Optional

# ============================================================
# КОНФИГУРАЦИЯ
# ============================================================

# Octobrowser API
OCTO_API_TOKEN = "your_token_here"
# 🔥 ПРАВИЛЬНЫЙ Base URL с /automation согласно официальной документации
# https://documenter.getpostman.com/view/1401428/UVC6i6eA
OCTO_API_BASE_URL = "https://app.octobrowser.net/api/v2/automation"

# CSV с данными
CSV_FILENAME = "data.csv"

# ============================================================
# OCTOBROWSER ФУНКЦИИ
# ============================================================

def create_profile():
    """Создать новый профиль через Octo API"""
    # 🔥 ПРАВИЛЬНЫЙ заголовок согласно официальной документации
    # https://docs.octobrowser.net/
    # > All requests require authentication via API token in the X-Octo-Api-Token header
    headers = {
        'X-Octo-Api-Token': OCTO_API_TOKEN,
        'Content-Type': 'application/json'
    }

    profile_data = {
        "title": f"Auto Profile {random.randint(1000, 9999)}",
        "fingerprint": {"os": "win"}
    }

    response = requests.post(
        f"{OCTO_API_BASE_URL}/profiles",
        headers=headers,
        json=profile_data
    )

    if response.status_code == 200:
        return response.json().get('uuid')
    return None

def start_profile(uuid: str):
    """Запустить профиль и получить debug_port"""
    headers = {
        'X-Octo-Api-Token': OCTO_API_TOKEN
    }

    response = requests.get(
        f"{OCTO_API_BASE_URL}/profiles/{uuid}/start",
        headers=headers
    )

    if response.status_code == 200:
        return response.json().get('debug_port')
    return None

def stop_profile(uuid: str):
    """Остановить профиль"""
    headers = {
        'X-Octo-Api-Token': OCTO_API_TOKEN
    }

    requests.get(f"{OCTO_API_BASE_URL}/profiles/{uuid}/stop", headers=headers)

# ============================================================
# ЗАГРУЗКА ДАННЫХ ИЗ CSV
# ============================================================

def load_data_from_csv(filename: str) -> List[Dict]:
    """Загрузить данные из CSV файла"""
    data_rows = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data_rows = list(reader)
    except FileNotFoundError:
        print(f"[ERROR] Файл {filename} не найден!")
    return data_rows

# ============================================================
# HELPER ФУНКЦИИ
# ============================================================

# === SMART BUTTON CLICK HANDLER ===
# Функция для устойчивого клика по кнопкам (независимо от порядка появления)
def smart_click_button(page, name: str, exact: bool = False):
    """Умный клик по кнопке с ожиданием появления"""
    locator = page.get_by_role("button", name=name, exact=exact)
    try:
        locator.wait_for(state="visible", timeout=30000)
        if locator.is_visible():
            print(f"[SMART CLICK] Кликаю кнопку: {name}")
            locator.click(delay=100)
            page.wait_for_load_state("networkidle", timeout=10000)
    except Exception as e:
        print(f"[SMART CLICK] Кнопка '{name}' не появилась за 30 сек или уже была обработана: {e}")

# === END SMART BUTTON HANDLER ===

# === SMART QUESTION-ANSWER HANDLER ===
# Функция для устойчивого ответа на вопросы (клик по heading → ответ на button)
def answer_question(page, heading: str, answer_button: str, exact: bool = False):
    """Ждёт появления вопроса (heading) и кликает по кнопке ответа"""
    print(f"[ANSWER] Жду вопрос: {heading}")
    heading_locator = page.get_by_role("heading", name=heading, exact=True)
    try:
        heading_locator.wait_for(state="visible", timeout=35000)
        print(f"[ANSWER] Вопрос появился: {heading} → отвечаю: {answer_button}")
        smart_click_button(page, answer_button, exact=exact)
    except Exception as e:
        print(f"[ANSWER] Вопрос '{heading}' не появился за 35 сек: {e}")

# === END SMART QUESTION-ANSWER HANDLER ===

# === OCTO BROWSER POPUP HANDLER ===
# Универсальный обработчик новых вкладок для Octo Browser
def wait_and_switch_to_popup(page, context, trigger_action=None, timeout=15000):
    """Надёжное переключение на новую вкладку в Octo Browser"""
    print("[POPUP] Ожидаю открытия новой вкладки...")
    before_pages = len(context.pages)

    # Выполнить действие, которое откроет попап
    if trigger_action:
        trigger_action()

    # Ждём появления новой вкладки (polling)
    import time
    start_time = time.time()
    while len(context.pages) <= before_pages:
        if (time.time() - start_time) * 1000 > timeout:
            raise Exception(f"[POPUP] Новая вкладка не открылась за {timeout}ms")
        time.sleep(0.1)

    # Берём последнюю открывшуюся вкладку
    new_page = context.pages[-1]

    # Проверка что это действительно новая вкладка
    if new_page == page:
        new_page = context.pages[-2] if len(context.pages) > 1 else context.pages[-1]

    # Гарантированно активируем и ждём загрузки
    new_page.bring_to_front()
    time.sleep(0.5)  # Дать время браузеру переключиться
    new_page.wait_for_load_state("domcontentloaded", timeout=30000)

    print(f"[POPUP] Переключился на новую вкладку: {new_page.url}")
    return new_page

# === END OCTO BROWSER POPUP HANDLER ===

# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ ИТЕРАЦИИ
# ============================================================

def run_automation_iteration(iteration_number: int, data_row: Dict):
    """
    Запуск одной итерации автоматизации с Playwright

    Args:
        iteration_number: Номер итерации
        data_row: Данные из CSV для этой итерации
    """
    profile_uuid = None
    browser = None
    context = None
    page = None

    print("\n" + "="*60)
    print(f"Итерация #{iteration_number}")
    print(f"Данные: {data_row}")
    print("="*60 + "\n")

    try:
        # Создать профиль
        profile_uuid = create_profile()
        if not profile_uuid:
            print("[ERROR] Не удалось создать профиль")
            return False

        # Запустить профиль
        debug_port = start_profile(profile_uuid)
        if not debug_port:
            print("[ERROR] Не удалось запустить профиль")
            return False

        # Подключиться к браузеру через CDP
        with sync_playwright() as p:
            cdp_url = f"http://127.0.0.1:{debug_port}"
            print(f"[CDP MODE] Подключение к Octobrowser через CDP: {cdp_url}")

            try:
                browser = p.chromium.connect_over_cdp(cdp_url)
                print("[OK] Playwright подключен к Octobrowser")
            except Exception as e:
                print(f"[ERROR] Не удалось подключиться к CDP: {e}")
                return False

            # Получить контекст и страницу
            if browser.contexts:
                context = browser.contexts[0]
                if context.pages:
                    page = context.pages[0]
                else:
                    page = context.new_page()
            else:
                print("[ERROR] Нет доступных контекстов браузера")
                return False

            print(f"[OK] Страница готова к автоматизации")

            # ============================================================
            # ПОЛЬЗОВАТЕЛЬСКИЙ КОД АВТОМАТИЗАЦИИ
            # ============================================================

            # Перейти на сайт
            page.goto("https://www.example.com", wait_until="domcontentloaded")

            # Заполнить форму данными из CSV
            page.get_by_role("textbox", name="Enter your ZIP code").fill(data_row.get("zip_code", "33071"))
            page.get_by_role("textbox", name="Email").fill(data_row.get("email", "test@gmail.com"))

            # Умный клик по кнопке
            smart_click_button(page, "See My Quotes")

            # Ответ на вопрос
            answer_question(page, "What is your age?", "25-34")

            # Еще один клик
            smart_click_button(page, "Continue")

            # ============================================================

            print(f"[OK] Итерация #{iteration_number} успешно завершена")
            return True

    except Exception as e:
        error_msg = str(e)
        if "target closed" in error_msg.lower() or "browser has been closed" in error_msg.lower():
            print(f"[!] ВНИМАНИЕ: Браузер был закрыт вручную!")
            print(f"Итерация #{iteration_number} прервана")
        elif "timeout" in error_msg.lower():
            print(f"[TIMEOUT] Элемент не найден в итерации #{iteration_number}")
            print(f"Возможно страница загружается слишком долго")
        else:
            print(f"[ERROR] Ошибка в итерации #{iteration_number}: {e}")

        import traceback
        traceback.print_exc()

        # Закрыть браузер и профиль ТОЛЬКО при ошибке
        print("[ERROR] Закрытие профиля из-за ошибки...")
        if browser:
            try:
                browser.close()
                print("[OK] Браузер закрыт")
            except:
                pass

        if profile_uuid:
            try:
                stop_profile(profile_uuid)
                print(f"[OK] Профиль {profile_uuid} остановлен")
            except:
                pass

        return False

# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    """Главная функция с мультизапуском"""
    try:
        # Загрузить данные из CSV
        data_rows = load_data_from_csv(CSV_FILENAME)

        if not data_rows:
            print("[ERROR] Нет данных для обработки!")
            return

        print(f"[INFO] Загружено {len(data_rows)} строк из {CSV_FILENAME}")

        # Запустить итерации
        for i, data_row in enumerate(data_rows, start=1):
            success = run_automation_iteration(i, data_row)

            if not success:
                print(f"[WARNING] Итерация {i} завершилась с ошибкой")

            # Пауза между итерациями
            if i < len(data_rows):
                pause = 5
                print(f"\n[PAUSE] Пауза {pause} секунд перед следующей итерацией...\n")
                time.sleep(pause)

        print("\n" + "="*60)
        print("ВСЕ ИТЕРАЦИИ ЗАВЕРШЕНЫ!")
        print("="*60)

    except KeyboardInterrupt:
        print("\n[!] Скрипт прерван пользователем")
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*60)
    print("Octobrowser Automation Script (Playwright SYNC)")
    print("="*60)
    main()
