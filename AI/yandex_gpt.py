from yandex_cloud_ml_sdk import YCloudML

class YandexGPTAssistant:
    def __init__(self, folder_id, api_key):
        # folder_id — идентификатор каталога (folder) из Yandex Cloud
        # api_key — секретная часть API-ключа сервисного аккаунта
        self.sdk = YCloudML(folder_id=folder_id, auth=api_key)
        # Можно выбрать 'yandexgpt' или 'yandexgpt-lite'
        self.model = self.sdk.models.completions('yandexgpt-lite')
        self.model = self.model.configure(temperature=0.6, max_tokens=200)

    def ask(self, query):
        result = self.model.run(query)
        return result[0].text if result else "Нет ответа от модели"
