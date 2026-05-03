from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame
)

from services.auth_service import login_user
from ui.windows.register_window import RegisterWindow
from ui.windows.main_window import MainWindow
from translations import translations


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.register_window = None
        self.main_window = None

        self.current_language = "uk"
        self.current_theme = "dark"

        self.setFixedSize(780, 640)
        self.setObjectName("authWindow")

        self.setup_ui()
        self.apply_styles()
        self.update_language()
        self.update_language_buttons()
        self.update_theme_button()

    def tr(self, key):
        return translations[self.current_language].get(key, key)

    def setup_ui(self):
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(28, 22, 28, 28)
        outer_layout.setSpacing(16)
        self.setLayout(outer_layout)

        # Top controls panel
        self.auth_top_panel = QFrame()
        self.auth_top_panel.setObjectName("authTopPanel")

        top_controls = QHBoxLayout()
        top_controls.setContentsMargins(0, 0, 0, 0)
        top_controls.setSpacing(12)

        # Language switcher
        self.language_frame = QFrame()
        self.language_frame.setObjectName("languageFrame")
        self.language_frame.setFixedWidth(120)

        language_layout = QVBoxLayout()
        language_layout.setContentsMargins(0, 0, 0, 0)
        language_layout.setSpacing(6)

        self.language_title = QLabel()
        self.language_title.setObjectName("languageTitle")
        self.language_title.setAlignment(Qt.AlignCenter)

        self.language_buttons_frame = QFrame()
        self.language_buttons_frame.setObjectName("languageButtonsFrame")

        lang_buttons_layout = QHBoxLayout()
        lang_buttons_layout.setContentsMargins(4, 4, 4, 4)
        lang_buttons_layout.setSpacing(4)

        self.ukr_button = QPushButton("UKR")
        self.ukr_button.setObjectName("langButton")
        self.ukr_button.setCheckable(True)
        self.ukr_button.setCursor(Qt.PointingHandCursor)

        self.eng_button = QPushButton("ENG")
        self.eng_button.setObjectName("langButton")
        self.eng_button.setCheckable(True)
        self.eng_button.setCursor(Qt.PointingHandCursor)

        lang_buttons_layout.addWidget(self.ukr_button)
        lang_buttons_layout.addWidget(self.eng_button)

        self.language_buttons_frame.setLayout(lang_buttons_layout)

        language_layout.addWidget(self.language_title)
        language_layout.addWidget(self.language_buttons_frame)

        self.language_frame.setLayout(language_layout)

        # Theme switcher
        self.theme_frame = QFrame()
        self.theme_frame.setObjectName("themeFrame")
        self.theme_frame.setFixedWidth(120)

        theme_layout = QVBoxLayout()
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.setSpacing(6)

        self.theme_title = QLabel()
        self.theme_title.setObjectName("themeTitle")
        self.theme_title.setAlignment(Qt.AlignCenter)

        self.theme_buttons_frame = QFrame()
        self.theme_buttons_frame.setObjectName("themeButtonsFrame")

        theme_button_layout = QHBoxLayout()
        theme_button_layout.setContentsMargins(4, 4, 4, 4)
        theme_button_layout.setSpacing(4)

        self.theme_button = QPushButton()
        self.theme_button.setObjectName("themeButton")
        self.theme_button.setCursor(Qt.PointingHandCursor)

        theme_button_layout.addWidget(self.theme_button)

        self.theme_buttons_frame.setLayout(theme_button_layout)

        theme_layout.addWidget(self.theme_title)
        theme_layout.addWidget(self.theme_buttons_frame)

        self.theme_frame.setLayout(theme_layout)

        top_controls.addStretch()
        top_controls.addWidget(self.language_frame)
        top_controls.addWidget(self.theme_frame)

        self.auth_top_panel.setLayout(top_controls)
        outer_layout.addWidget(self.auth_top_panel)

        # Form frame
        self.form_frame = QFrame()
        self.form_frame.setObjectName("sectionFrame")
        self.form_frame.setMaximumWidth(500)

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(34, 34, 34, 34)
        form_layout.setSpacing(18)

        self.title_label = QLabel()
        self.title_label.setObjectName("mainTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 22px; font-weight: 700;")

        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("subTitle")
        self.subtitle_label.setAlignment(Qt.AlignCenter)

        self.email_input = QLineEdit()
        self.email_input.setObjectName("authInput")
        self.email_input.setMinimumHeight(46)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("authInput")
        self.password_input.setMinimumHeight(46)

        self.login_button = QPushButton()
        self.login_button.setObjectName("primaryButton")
        self.login_button.setMinimumHeight(46)
        self.login_button.setCursor(Qt.PointingHandCursor)

        self.register_button = QPushButton()
        self.register_button.setObjectName("secondaryButton")
        self.register_button.setMinimumHeight(46)
        self.register_button.setCursor(Qt.PointingHandCursor)

        form_layout.addWidget(self.title_label)
        form_layout.addWidget(self.subtitle_label)
        form_layout.addSpacing(8)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.password_input)
        form_layout.addSpacing(8)
        form_layout.addWidget(self.login_button)
        form_layout.addWidget(self.register_button)

        self.form_frame.setLayout(form_layout)

        outer_layout.addStretch()
        outer_layout.addWidget(self.form_frame, alignment=Qt.AlignCenter)
        outer_layout.addStretch()

        # Signals
        self.login_button.clicked.connect(self.handle_login)
        self.register_button.clicked.connect(self.open_register)

        self.ukr_button.clicked.connect(lambda: self.change_language("uk"))
        self.eng_button.clicked.connect(lambda: self.change_language("en"))
        self.theme_button.clicked.connect(self.toggle_theme)

    def apply_styles(self):
        try:
            style_path = "styles/light.qss" if self.current_theme == "light" else "styles/main.qss"

            with open(style_path, "r", encoding="utf-8") as file:
                self.setStyleSheet(file.read())

        except Exception as e:
            print("Style loading error:", e)

    def update_language(self):
        self.setWindowTitle(self.tr("login_window_title"))

        self.language_title.setText(self.tr("language"))
        self.theme_title.setText(self.tr("theme"))

        self.title_label.setText(self.tr("app_title"))
        self.subtitle_label.setText(self.tr("login_subtitle"))

        self.email_input.setPlaceholderText(self.tr("email"))
        self.password_input.setPlaceholderText(self.tr("password"))

        self.login_button.setText(self.tr("login"))
        self.register_button.setText(self.tr("create_account"))

        self.update_language_buttons()
        self.update_theme_button()

    def change_language(self, language):
        if language == self.current_language:
            self.update_language_buttons()
            return

        self.current_language = language
        self.update_language()

    def update_language_buttons(self):
        self.ukr_button.setChecked(self.current_language == "uk")
        self.eng_button.setChecked(self.current_language == "en")

        for button in [self.ukr_button, self.eng_button]:
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_styles()
        self.update_theme_button()

    def update_theme_button(self):
        if self.current_theme == "dark":
            self.theme_button.setText("☀️ Light")
        else:
            self.theme_button.setText("🌙 Dark")

        self.theme_button.style().unpolish(self.theme_button)
        self.theme_button.style().polish(self.theme_button)
        self.theme_button.update()

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        success, result = login_user(email, password)

        if success:
            self.main_window = MainWindow(
                language=self.current_language,
                theme=self.current_theme
            )
            self.main_window.current_user = result
            self.main_window.show()
            self.close()
        else:
            self.show_message(
                self.tr("login_error_title"),
                result,
                QMessageBox.Warning
            )

    def show_message(self, title, text, icon=QMessageBox.Information):
        msg_box = QMessageBox(self)
        msg_box.setObjectName("authMessageBox")
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.button(QMessageBox.Ok).setText("OK")
        msg_box.exec()

    def open_register(self):
        self.register_window = RegisterWindow(login_window=self)
        self.register_window.current_language = self.current_language
        self.register_window.current_theme = self.current_theme

        if hasattr(self.register_window, "apply_styles"):
            self.register_window.apply_styles()

        if hasattr(self.register_window, "update_language"):
            self.register_window.update_language()

        self.register_window.show()
        self.hide()