# Файл: System/system_controller.py

import os
from datetime import datetime
from PIL import ImageGrab

# Импорты для управления громкостью
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER

class SystemController:
    """
    Отвечает за управление функциями ОС: скриншоты, громкость и т.д.
    """
    def __init__(self):
        # --- Инициализация для скриншотов ---
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.screenshots_dir = os.path.join(project_root, "Screenshots")
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)

        # --- ИНИЦИАЛИЗАЦИЯ ДЛЯ УПРАВЛЕНИЯ ГРОМКОСТЬЮ ---
        self.volume = None
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            # Эта ошибка может возникнуть, если вы запускаете на ОС, отличной от Windows
            print(f"Предупреждение: не удалось инициализировать управление звуком. Ошибка: {e}")
            print("Функции управления громкостью будут недоступны.")

    def take_screenshot(self) -> str:
        """Делает скриншот и сохраняет его."""
        try:
            screenshot = ImageGrab.grab()
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_path = os.path.join(self.screenshots_dir, f"screenshot_{timestamp}.png")
            screenshot.save(file_path)
            return "Скриншот успешно сохранен!"
        except Exception as e:
            return f"Не удалось сделать скриншот: {e}"

    # --- НОВЫЕ МЕТОДЫ ДЛЯ ГРОМКОСТИ ---
    def set_volume(self, level: int) -> str:
        """Устанавливает громкость системы на уровень от 0 до 100."""
        if not self.volume:
            return "Управление громкостью недоступно на вашей системе."
        
        if 0 <= level <= 100:
            self.volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            return f"Громкость установлена на {level} процентов."
        return "Неверный уровень громкости. Укажите значение от 0 до 100."

    def change_volume(self, change_by_percent: int) -> str:
        """Изменяет громкость на указанное количество процентов (+ или -)."""
        if not self.volume:
            return "Управление громкостью недоступно на вашей системе."

        current_scalar = self.volume.GetMasterVolumeLevelScalar()
        current_level = round(current_scalar * 100)
        new_level = current_level + change_by_percent
        # Ограничиваем итоговый уровень громкости диапазоном 0-100
        new_level = max(0, min(100, new_level))
        
        return self.set_volume(new_level)
