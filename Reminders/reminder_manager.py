import datetime
import time
import threading

class ReminderManager:
    def __init__(self, voice_output):
        self.reminders = []
        self.voice_output = voice_output
        self.lock = threading.Lock()
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self._check_reminders_loop, daemon=True)
        self.thread.start()

    def add_reminder(self, text: str, remind_at: datetime.datetime):
        """Добавляет новое напоминание в список."""
        with self.lock:
            self.reminders.append({"text": text, "time": remind_at, "triggered": False})
        time_str = remind_at.strftime('%H:%M')
        return f"Хорошо, я напомню вам в {time_str}: {text}."

    def _check_reminders_loop(self):
        while not self._stop_event.is_set():
            now = datetime.datetime.now()
            reminders_to_trigger = []

            with self.lock:
                for reminder in self.reminders:
                    if not reminder["triggered"] and now >= reminder["time"]:
                        reminder_text = f"Напоминаю: {reminder['text']}"
                        print(f"--- СРАБОТАЛО НАПОМИНАНИЕ: {reminder_text} ---")
                        self.voice_output.play("reminders.wav", text=reminder_text)
                        reminder["triggered"] = True
            with self.lock:
                self.reminders = [r for r in self.reminders if not r["triggered"]]

            time.sleep(5)

    def stop(self):
        """Останавливает фоновый поток при закрытии программы."""
        self._stop_event.set()
