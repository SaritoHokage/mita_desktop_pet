from libretranslatepy import LibreTranslateAPI

class Translator:
    def __init__(self, api_url="https://libretranslate.com/", api_key=None):
        self.lt = LibreTranslateAPI(api_url, api_key=api_key)

    def translate(self, text, target_lang="en", source_lang="auto"):

        try:
            result = self.lt.translate(text, source=source_lang, target=target_lang)
            return result
        except Exception as e:
            return f"Ошибка перевода: {e}"

    def detect_language(self, text):
        try:
            detected = self.lt.detect(text)
            if detected and isinstance(detected, list):
                return detected[0].get("language", "unknown")
            return "unknown"
        except Exception as e:
            return f"Ошибка определения языка: {e}"

    def get_languages(self):
        try:
            return self.lt.languages()
        except Exception as e:
            return f"Ошибка получения языков: {e}"
