import speech_recognition as sr

class VoiceInput:
    def __init__(self, language="ru-RU"):
        self.r = sr.Recognizer()
        self.mic = sr.Microphone()
        self.language = language
        self.r.pause_threshold = 1.5

        print("Адаптация к фоновому шуму...")
        with self.mic as source:
            self.r.adjust_for_ambient_noise(source, duration=1.5)
        print("Готов слушать.")

    def listen(self) -> str | None:
        with self.mic as source:
            print("Слушаю...")
            try:
                audio = self.r.listen(source, phrase_time_limit=15)
                print("Распознаю вашу команду...")
                command = self.r.recognize_google(audio, language=self.language)
                print(f"Вы сказали: {command}")
                return command.lower()
            except sr.UnknownValueError:
                print("Не удалось распознать речь.")
                return None
            except sr.RequestError as e:
                print(f"Ошибка сервиса распознавания Google: {e}")
                return None
            except Exception as e:
                print(f"Неизвестная ошибка в VoiceInput: {e}")
                return None
