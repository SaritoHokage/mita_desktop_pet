import os
import platform
import subprocess
import webbrowser

class WorkspaceManager:
    def __init__(self):
        self.apps = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Users\yegor\AppData\Local\Programs\Perplexity\Perplexity.exe",
            r"C:\Users\yegor\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            r"C:\Users\yegor\AppData\Local\Programs\YandexMusic\Яндекс Музыка.exe"
        ]
        self.folders = [

        ]
        self.websites = [
            "https://mail.google.com",
            "https://github.com"
        ]

    def open_apps(self):
        system = platform.system()
        for app in self.apps:
            try:
                if system == "Windows":
                    os.startfile(app)
                elif system == "Darwin":
                    subprocess.Popen(["open", app])
                else:
                    subprocess.Popen([app])
            except Exception as e:
                print(f"Ошибка открытия приложения {app}: {e}")

    def open_folders(self):
        system = platform.system()
        for folder in self.folders:
            try:
                if system == "Windows":
                    os.startfile(folder)
                elif system == "Darwin":
                    subprocess.Popen(["open", folder])
                else:
                    subprocess.Popen(["xdg-open", folder])
            except Exception as e:
                print(f"Ошибка открытия папки {folder}: {e}")

    def open_websites(self):
        for site in self.websites:
            try:
                webbrowser.open(site)
            except Exception as e:
                print(f"Ошибка открытия сайта {site}: {e}")

    def prepare_workspace(self):
        self.open_apps()
        self.open_folders()
        self.open_websites()
