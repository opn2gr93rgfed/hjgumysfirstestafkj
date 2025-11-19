"""
Provider: smart_no_api
Runner без API зависимостей
"""

from typing import Optional, Callable
import subprocess
import threading
import sys
import os


class Runner:
    """Раннер для выполнения скриптов без API"""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.output_callback: Optional[Callable] = None
        self.is_running = False

    def set_output_callback(self, callback: Callable):
        """Установить callback для вывода"""
        self.output_callback = callback

    def run(self, script_path: str):
        """Запустить скрипт"""
        if self.is_running:
            if self.output_callback:
                self.output_callback("[ERROR] Скрипт уже запущен")
            return

        self.is_running = True

        def _run():
            try:
                env = os.environ.copy()

                self.process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    env=env
                )

                for line in self.process.stdout:
                    if self.output_callback:
                        self.output_callback(line.rstrip())

                self.process.wait()

                if self.output_callback:
                    self.output_callback(f"\n[DONE] Скрипт завершен с кодом {self.process.returncode}")

            except Exception as e:
                if self.output_callback:
                    self.output_callback(f"[ERROR] {e}")
            finally:
                self.is_running = False
                self.process = None

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def stop(self):
        """Остановить скрипт"""
        if self.process and self.is_running:
            self.process.terminate()
            self.is_running = False
            if self.output_callback:
                self.output_callback("[STOP] Скрипт остановлен")
