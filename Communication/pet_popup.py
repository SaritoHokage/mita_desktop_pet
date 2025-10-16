import sys
import os
import pygame
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget
from PySide6.QtGui import QPixmap, QFontMetrics, QFontDatabase, QFont
from PySide6.QtCore import Qt, QTimer, QPoint

def get_resource_path(relative_path):
    try:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    except NameError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class PetPopup(QMainWindow):
    def __init__(self, text, audio_path,
                 image_closed=get_resource_path("Resources/img/pet_closed.png"),
                 image_open=get_resource_path("Resources/img/pet_open.png"),
                 background_path=get_resource_path("Resources/img/background.png")):
        super().__init__()

        self.text_to_display = text
        self.audio_path = audio_path
        self.background_path = background_path
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        screen_geometry = QApplication.primaryScreen().geometry()
        pet_size = min(int(screen_geometry.width() / 7), 260)
        self.pet_size = pet_size
        textbox_width = int(pet_size * 1.5)
        self.margin = 24

        font_path = get_resource_path("Resources/fonts/BubbleSans-Regular.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        self.custom_font = QFont("Arial", 12)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                self.custom_font = QFont(font_families[0], 12, QFont.Bold)
        else:

            print(f"ВНИМАНИЕ: Не удалось загрузить шрифт. Проверьте путь: {font_path}")
        
        font_metrics = QFontMetrics(self.custom_font)
        self.v_padding = 25 + 20 
        self.min_bg_height = font_metrics.height() * 2 + self.v_padding
        
        self.bg_pixmap_template = QPixmap(self.background_path)
        initial_bg_pixmap = self.bg_pixmap_template.scaled(
            textbox_width + self.margin * 2, int(self.min_bg_height),
            Qt.IgnoreAspectRatio, Qt.SmoothTransformation
        )

        self.pet_closed_pixmap = QPixmap(image_closed).scaled(pet_size, pet_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.pet_open_pixmap = QPixmap(image_open).scaled(pet_size, pet_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.background_label = QLabel(self.central_widget)
        self.background_label.setPixmap(initial_bg_pixmap)
        self.pet_label = QLabel(self.central_widget)
        self.pet_label.setPixmap(self.pet_closed_pixmap)
        self.pet_label.setAlignment(Qt.AlignCenter)
    
        common_style = f"""
            color: #ffffff; 
            background-color: transparent; 
            padding-top: 25px; 
            padding-left: 20px; 
            padding-right: 20px; 
            padding-bottom: 20px;
        """
        shadow_style = "color: #8B0000;" + common_style

        self.shadow_label = QLabel(self.central_widget)
        self.shadow_label.setWordWrap(True)
        self.shadow_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.shadow_label.setFont(self.custom_font)
        self.shadow_label.setStyleSheet(shadow_style)
        self.text_label = QLabel(self.central_widget)
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.text_label.setFont(self.custom_font)
        self.text_label.setStyleSheet(common_style.replace("#ffffff", "#ffffff"))
        initial_window_width = initial_bg_pixmap.width()
        initial_window_height = (self.pet_size - self.margin) + self.min_bg_height
        self.pet_label.setGeometry(
            (initial_window_width - self.pet_size) // 2, self.margin, 
            self.pet_size, self.pet_size
        )
        bg_geom = QPoint(0, self.pet_size - self.margin)
        self.background_label.setGeometry(bg_geom.x(), bg_geom.y(), initial_bg_pixmap.width(), initial_bg_pixmap.height())
        
        text_geom = self.background_label.geometry()
        self.text_label.setGeometry(text_geom)
        self.shadow_label.setGeometry(text_geom.translated(1, 1))
        self.resize(initial_window_width, initial_window_height)
        x = screen_geometry.width() - initial_window_width - 40
        y = 40
        self.move(x, y)
        self._drag_pos = None
        self._mouth_open = False
        self.mouth_timer = QTimer(self)
        self.mouth_timer.timeout.connect(self._animate_mouth)
        self.typing_timer = QTimer(self)
        self.typing_timer.timeout.connect(self._add_char)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos: self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event): self._drag_pos = None

    def _resize_to_fit_text(self):
        h_padding = 40
        font_metrics = QFontMetrics(self.text_label.font())
        bounding_rect = font_metrics.boundingRect(0, 0, self.background_label.width() - h_padding, 9999, Qt.AlignHCenter | Qt.TextWordWrap, self.current_text)
        required_height = bounding_rect.height() + self.v_padding
        new_bg_height = max(self.min_bg_height, required_height)
        if new_bg_height <= self.background_label.height(): return
        new_bg_pixmap = self.bg_pixmap_template.scaled(self.background_label.width(), int(new_bg_height), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        new_window_height = (self.pet_size - self.margin) + new_bg_height
        self.setFixedHeight(int(new_window_height))
        self.background_label.setFixedHeight(int(new_bg_height))
        self.background_label.setPixmap(new_bg_pixmap)
        text_geom = self.background_label.geometry()
        self.text_label.setGeometry(text_geom)
        self.shadow_label.setGeometry(text_geom.translated(1, 1))

    def start_logic(self):
        try:
            if not isinstance(self.audio_path, str) or not os.path.exists(self.audio_path):
                self._type_text(instant=True)
                return
            pygame.mixer.init()
            sound = pygame.mixer.Sound(self.audio_path)
            duration = sound.get_length()
            sound.play()
            self.mouth_timer.start(170)
            QTimer.singleShot(int(duration * 1000), self.mouth_timer.stop)
            QTimer.singleShot(int(duration * 1000), lambda: self.pet_label.setPixmap(self.pet_closed_pixmap))
            self._type_text()
        except Exception as e:
            print(f"Ошибка воспроизведения или анимации: {e}")
            self._type_text(instant=True)

    def _animate_mouth(self):
        self._mouth_open = not self._mouth_open
        pixmap = self.pet_open_pixmap if self._mouth_open else self.pet_closed_pixmap
        self.pet_label.setPixmap(pixmap)

    def _type_text(self, instant=False):
        if instant:
            self.current_text = self.text_to_display
            self.text_label.setText(self.current_text)
            self.shadow_label.setText(self.current_text)
            self._resize_to_fit_text()
            QTimer.singleShot(5000, self.close)
            return
        self.current_text = ""
        self.char_index = 0
        self.typing_timer.start(50)

    def _add_char(self):
        if self.char_index < len(self.text_to_display):
            self.current_text += self.text_to_display[self.char_index]
            self.text_label.setText(self.current_text)
            self.shadow_label.setText(self.current_text)
            self.char_index += 1
            self._resize_to_fit_text()
        else:
            self.typing_timer.stop()
            QTimer.singleShot(5000, self.close)

def show_pet_popup_with_voice_and_typing(text, audio_path):
    try:
        app = QApplication.instance()
        if app is None: app = QApplication(sys.argv)
        popup = PetPopup(text, audio_path)
        popup.show()
        QTimer.singleShot(10, popup.start_logic)
        sys.exit(app.exec())
    except Exception as e:
        print(f"Ошибка создания окна питомца PySide6: {e}")
