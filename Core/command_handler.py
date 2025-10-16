import os
import re
import platform
import subprocess
import threading
import time
from datetime import datetime, timedelta
from AI.weather import Weather
from AI.translate import Translator
from AI.selenium_youtube import YouTubePlayer
from AI.yandex_gpt import YandexGPTAssistant
from Core.workspace_manager import WorkspaceManager
from System.system_controller import SystemController

class CommandHandler:
    def __init__(self, voice_output, reminder_manager, weather_api_key=None, translate_api_key=None, folder_id=None, yandex_gpt_api_key=None):
        self.voice_output = voice_output
        self.reminder_manager = reminder_manager
        self.weather = Weather(weather_api_key) if weather_api_key else None
        self.translator = Translator(api_key=translate_api_key)
        self.youtube = YouTubePlayer()
        self.workspace = WorkspaceManager()
        self.assistant = YandexGPTAssistant(folder_id=folder_id, api_key=yandex_gpt_api_key)
        self.system_controller = SystemController()

        self.ai_mode = False
        self.is_listening = False
        self.last_heard_time = 0
        self.WAKE_WORD = "мита"
        self.LISTENING_TIMEOUT = 10
        self.youtube_search_results = []

    def run_command(self, command: str):
        command = command.lower().strip()
        if not command: return
        current_time = time.time()

        if "включи режим ассистента" in command:
            self.ai_mode, self.is_listening = True, False
            self.voice_output.play("assistent.wav", text="Режим ИИ-ассистента активирован")
            return
        if "выключи режим ассистента" in command or "отключи ассистента" in command:
            self.ai_mode, self.is_listening = False, False
            self.voice_output.play("deactivation.wav", text="Режим ИИ-ассистента отключён")
            return

        if self.WAKE_WORD in command:
            self.is_listening = True
            self.last_heard_time = current_time
            command = command.replace(self.WAKE_WORD, "", 1).strip()
            if not command:
                self.voice_output.play("activation.wav", text="Слушаю...")
                return
        else:
            if self.is_listening and (current_time - self.last_heard_time > self.LISTENING_TIMEOUT):
                self.is_listening = False
                self.voice_output.play("timeout.wav", text="")
                return
            if not self.ai_mode and not self.is_listening: return
        
        if self.is_listening: self.last_heard_time = current_time
        if self.ai_mode:
            answer = self.assistant.ask(command)
            self.voice_output.play("assistant_answer.wav", text=answer)
            return
        
        if self.youtube_search_results and ("включи" in command or "запусти" in command or "выбери" in command):
            video_index = self._extract_video_number(command)
            if video_index is not None and 0 <= video_index < len(self.youtube_search_results):
                selected_video = self.youtube_search_results[video_index]
                
                self.youtube.close_search_window()

                self.voice_output.play("vkl.wav", text=f"Отлично, включаю видео.")
                
                threading.Thread(target=self.youtube.play_video_by_url, args=(selected_video['url'],), daemon=True).start()
                
                self.youtube_search_results = []
                return
        
        print(f"Выполняю команду: {command}")
        
        if "включи видео" in command or "найди видео" in command or "youtube" in command:
            query = self._extract_youtube_query(command)
            if not query:
                self.voice_output.play("error.wav", text="Пожалуйста, уточните, что найти.")
                return
            
            self.voice_output.play("search.wav", text=f"Ищу на YouTube: {query}")
            self.youtube_search_results = self.youtube.search_videos(query)
            
            if self.youtube_search_results:
                self.voice_output.play("searchvideo.wav", text="Вот что я нашла. Какое видео включить?")
            else:
                self.voice_output.play("error.wav", text="К сожалению, ничего не нашла по этому запросу.")
        elif "сделай скриншот" in command or "снимок экрана" in command:
            result_text = self.system_controller.take_screenshot()
            self.voice_output.play("ok.wav", text=result_text)
        elif "напомни" in command:
            text, remind_time = self._parse_reminder_command(command)
            if remind_time:
                response = self.reminder_manager.add_reminder(text, remind_time)
                self.voice_output.play("ok.wav", text=response)
            else:
                self.voice_output.play("error.wav", text="Не удалось распознать время для напоминания.")
        elif "громкость на" in command or "установи громкость" in command:
            level = self._extract_number(command)
            if level is not None:
                result = self.system_controller.set_volume(level)
                self.voice_output.play("ok.wav", text=result)
            else:
                self.voice_output.play("error.wav", text="Не удалось распознать уровень громкости.")
        elif "громче" in command:
            result = self.system_controller.change_volume(10)
            self.voice_output.play("ok.wav", text=result)
        elif "тише" in command:
            result = self.system_controller.change_volume(-10)
            self.voice_output.play("ok.wav", text=result)
        elif "погода" in command:
            city = self._extract_city(command)
            weather_data = self.weather.get_weather(city)
            if "error" in weather_data:
                self.voice_output.play("error.wav", text=weather_data["error"])
            else:
                result_text = f"В городе {weather_data['city']} сейчас {weather_data['description']}, температура {weather_data['temp']}°."
                self.voice_output.play("weather.wav", text=result_text)
        elif "переведи" in command:
            text, target = self._extract_translate_params(command)
            result = self.translator.translate(text, target_lang=target)
            self.voice_output.play("ok.wav", text=f"Перевод: {result}")
        elif "подготовь рабочее пространство" in command:
            self.voice_output.play("secondopen.wav", text="Готовлю рабочее пространство")
            self.workspace.prepare_workspace()
        elif "выключи компьютер" in command:
            self.voice_output.play("deactivation.wav", text="Выключаю компьютер")
            self.shutdown()
        elif "браузер" in command or "chrome" in command:
            self.voice_output.play("open2.wav", text="Открываю браузер")
            threading.Thread(target=self.open_browser, daemon=True).start()
        else:
            self.voice_output.play("unknown_command.wav", text="Команда не распознана")

    def _extract_video_number(self, command: str) -> int | None:
        number_map = {"первое": 0, "первый": 0, "1": 0, "один": 0,
                      "второе": 1, "второй": 1, "2": 1, "два": 1,
                      "третье": 2, "третий": 2, "3": 2, "три": 2,
                      "четвертое": 3, "четвёртый": 3, "4": 3, "четыре": 3,
                      "пятое": 4, "пятый": 4, "5": 4, "пять": 4}
        for word in command.split():
            if word in number_map:
                return number_map[word]
        return None

    def _parse_reminder_command(self, command: str) -> tuple[str | None, datetime | None]:
        now = datetime.now()
        match_after = re.search(r'через (\d+) (минут|минуту|час|часа)', command)
        if match_after:
            amount, unit = int(match_after.group(1)), match_after.group(2)
            delta = timedelta(minutes=amount) if "минут" in unit else timedelta(hours=amount)
            text = command.split(match_after.group(0), 1)[1].strip()
            return text, now + delta
        match_at = re.search(r'в (\d{1,2})[:\s](\d{2})|в (\d{1,2}) час', command)
        if match_at:
            hour, minute = (int(match_at.group(3)), 0) if match_at.group(3) else map(int, match_at.groups()[:2])
            remind_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if remind_time < now:
                remind_time += timedelta(days=1)
            text = command.split(match_at.group(0), 1)[1].strip()
            return text, remind_time
        return None, None

    def _extract_number(self, text: str) -> int | None:
        found = re.findall(r'\d+', text)
        return int(found[0]) if found else None

    def _extract_city(self, command: str) -> str:
        parts = command.split()
        if "в" in parts:
            try:
                idx = parts.index("в")
                if idx + 1 < len(parts):
                    return parts[idx + 1].capitalize()
            except ValueError:
                pass
        return "Moscow"

    def _extract_translate_params(self, command: str) -> tuple[str, str]:
        parts = command.split()
        if "переведи" in parts and "на" in parts:
            try:
                idx_text_start = parts.index("переведи") + 1
                idx_text_end = parts.index("на")
                idx_lang = idx_text_end + 1
                text = " ".join(parts[idx_text_start:idx_text_end])
                lang_word = parts[idx_lang] if idx_lang < len(parts) else "английский"
                lang_map = {"русский": "ru", "английский": "en", "немецкий": "de", "французский": "fr"}
                target_lang = lang_map.get(lang_word.lower(), "en")
                return text, target_lang
            except ValueError: pass
        return command.replace("переведи", "").strip(), "en"

    def _extract_youtube_query(self, command: str) -> str:
        triggers = ["включи видео", "найди видео", "youtube"]
        for trigger in triggers:
            if trigger in command:
                return command.split(trigger, 1)[1].strip()
        return ""

    def open_browser(self):
        system = platform.system()
        try:
            if system == "Windows": os.startfile("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
            elif system == "Darwin": subprocess.Popen(["open", "-a", "Safari"])
            else: subprocess.Popen(["xdg-open", "http://google.com"])
        except Exception as e:
            print(f"Ошибка открытия браузера: {e}")

    def shutdown(self):
        system = platform.system()
        try:
            if system == "Windows": os.system("shutdown /s /t 1")
            elif system == "Darwin": os.system("sudo shutdown -h now")
            else: os.system("shutdown now")
        except Exception as e:
            print(f"Ошибка выключения: {e}")
