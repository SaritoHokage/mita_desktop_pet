import os
import multiprocessing
import pygame

from Communication.pet_popup import show_pet_popup_with_voice_and_typing

def _show_pet_popup_in_process(text, audio_path):
    try:
        pygame.mixer.quit()
        pygame.mixer.init()
        show_pet_popup_with_voice_and_typing(text, audio_path)
    except Exception as e:
        print(f"Ошибка в процессе питомца: {e}")

class VoiceOutput:
    def __init__(self, voices_dir):
        self.voices_dir = voices_dir
        try:
            pygame.mixer.init()
        except Exception:
            pygame.mixer.quit()
            pygame.mixer.init()

    def play(self, filename, block=False, text=""):
        if not isinstance(filename, str):
            print(f"Ошибка: имя файла должно быть строкой, а не {type(filename)}")
            return
        
        path = os.path.join(self.voices_dir, filename)
        if not isinstance(path, str) or not os.path.exists(path):
            print(f"Файл не найден или путь не строка: {path}")
            return

        ext = os.path.splitext(path)[1].lower()
        if ext not in (".wav", ".ogg", ".mp3"):
            print(f"Формат {ext} не поддерживается. Используйте WAV, OGG или MP3.")
            return

        try:
            proc = multiprocessing.Process(
                target=_show_pet_popup_in_process,
                args=(text, path),
                daemon=True
            )
            proc.start()
        except Exception as e:
            print(f"Ошибка запуска процесса питомца: {e}")
