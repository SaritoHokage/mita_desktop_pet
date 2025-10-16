# Файл: AI/selenium_youtube.py

import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class YouTubePlayer:
    def __init__(self):
        self.search_driver = None

    def _get_driver(self):
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--start-maximized")

        return webdriver.Chrome(service=service, options=options)

    def search_videos(self, query: str, max_results: int = 5) -> list[dict]:
        if self.search_driver:
            self.close_search_window()

        self.search_driver = self._get_driver()
        results = []
        try:
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            self.search_driver.get(search_url)

            WebDriverWait(self.search_driver, 10).until(
                EC.presence_of_element_located((By.ID, "video-title"))
            )
            time.sleep(2)

            soup = BeautifulSoup(self.search_driver.page_source, "html.parser")
            video_links = soup.find_all('a', id='video-title', limit=max_results)

            for link in video_links:
                title = link.get('title')
                url = "https://www.youtube.com" + link.get('href')
                if title and url.startswith("https://www.youtube.com/watch"):
                    results.append({'title': title, 'url': url})
            
            return results
        except Exception as e:
            print(f"Ошибка при поиске видео: {e}")
            self.close_search_window()
            return []

    def close_search_window(self):
        if self.search_driver:
            try:
                self.search_driver.quit()
            except Exception:
                pass
            finally:
                self.search_driver = None

    def play_video_by_url(self, url: str):
        driver = self._get_driver()
        try:
            driver.get(url)
            wait = WebDriverWait(driver, 20)

            try:
                consent_button_xpath = "//*[contains(text(), 'Принять все') or contains(text(), 'Accept all')]"
                consent_button = wait.until(EC.element_to_be_clickable((By.XPATH, consent_button_xpath)))
                consent_button.click()
                time.sleep(1)
            except Exception:
                pass

            play_button_selector = ".ytp-large-play-button, #movie_player"
            play_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, play_button_selector)))
            play_element.click()
            
            while True:
                if not driver.window_handles:
                    break
                time.sleep(5)

        except Exception as e:
            print(f"Воспроизведение было прервано или произошла ошибка: {e}")
        finally:
            driver.quit()
