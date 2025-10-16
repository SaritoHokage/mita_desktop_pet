# Файл: AI/weather.py

import requests

class Weather:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_weather(self, city="Moscow", lang="ru"):
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": lang
        }
        try:
            response = requests.get(url, params=params, timeout=5)
            data = response.json()

            if response.status_code != 200:
                error_message = data.get("message", "неизвестная ошибка API")
                if response.status_code == 404:
                    return {"error": f"Я не смог найти город {city}."}
                return {"error": f"Ошибка от сервиса погоды: {error_message}"}

            description = data["weather"][0]["description"]
            temp = round(data["main"]["temp"]) 
            
            return {
                "city": data["name"],
                "description": description,
                "temp": temp
            }
        except requests.exceptions.RequestException as e:
            return {"error": f"Ошибка сети при запросе погоды. Проверьте подключение."}
        except Exception as e:
            return {"error": f"Неизвестная ошибка при получении погоды: {e}"}
