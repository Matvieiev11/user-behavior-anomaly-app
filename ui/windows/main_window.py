from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QMessageBox
)

from translations import translations
from ui.pages.dashboard_page import DashboardPage
from ui.pages.analysis_page import AnalysisPage
from ui.pages.history_page import HistoryPage

class MainWindow(QMainWindow):
    def __init__(self, language="uk", theme="dark"):
        super().__init__()

        self.current_language = language
        self.current_theme = theme

        self.setup_ui()
        self.apply_styles()
        self.showFullScreen()
        self.update_language()
        self.update_active_button(0)
        self.update_language_buttons()
        self.update_theme_button()

    def tr(self, key):
        return translations[self.current_language].get(key, key)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        self.setup_pages()
        self.connect_signals()

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(130)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(12, 20, 12, 20)
        sidebar_layout.setSpacing(18)

        # Language switcher
        self.language_frame = QFrame()
        self.language_frame.setObjectName("languageFrame")

        language_layout = QVBoxLayout()
        language_layout.setContentsMargins(0, 0, 0, 0)
        language_layout.setSpacing(8)

        self.language_title = QLabel()
        self.language_title.setObjectName("languageTitle")
        self.language_title.setAlignment(Qt.AlignCenter)
        language_layout.addWidget(self.language_title)

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
        language_layout.addWidget(self.language_buttons_frame)

        self.language_frame.setLayout(language_layout)
        sidebar_layout.addWidget(self.language_frame)

        # Menu title
        self.menu_title = QLabel()
        self.menu_title.setObjectName("menuTitle")
        self.menu_title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(self.menu_title)

        # Navigation buttons
        self.dashboard_btn = QPushButton()
        self.dashboard_btn.setObjectName("sideButton")
        self.dashboard_btn.setCursor(Qt.PointingHandCursor)
        sidebar_layout.addWidget(self.dashboard_btn)

        self.analytics_btn = QPushButton()
        self.analytics_btn.setObjectName("sideButton")
        self.analytics_btn.setCursor(Qt.PointingHandCursor)
        sidebar_layout.addWidget(self.analytics_btn)

        self.history_btn = QPushButton()
        self.history_btn.setObjectName("sideButton")
        self.history_btn.setCursor(Qt.PointingHandCursor)
        sidebar_layout.addWidget(self.history_btn)

        sidebar_layout.addStretch()

        # Theme switcher
        self.theme_frame = QFrame()
        self.theme_frame.setObjectName("themeFrame")

        theme_layout = QVBoxLayout()
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.setSpacing(8)

        self.theme_title = QLabel()
        self.theme_title.setObjectName("themeTitle")
        self.theme_title.setAlignment(Qt.AlignCenter)
        theme_layout.addWidget(self.theme_title)

        self.theme_button = QPushButton()
        self.theme_button.setObjectName("themeButton")
        self.theme_button.setCursor(Qt.PointingHandCursor)
        theme_layout.addWidget(self.theme_button)

        self.theme_frame.setLayout(theme_layout)
        sidebar_layout.addWidget(self.theme_frame)

        # Logout button
        self.logout_button = QPushButton()
        self.logout_button.setObjectName("sideButtonDanger")
        self.logout_button.setCursor(Qt.PointingHandCursor)
        sidebar_layout.addWidget(self.logout_button)

        sidebar.setLayout(sidebar_layout)
        return sidebar

    def setup_pages(self):
        self.dashboard_page = DashboardPage()
        self.analysis_page = AnalysisPage()
        self.history_page = HistoryPage()

        self.dashboard_page.main_window = self
        self.analysis_page.main_window = self
        self.history_page.main_window = self

        self.analysis_page.risk_gauge.set_theme(self.current_theme)
        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.analysis_page)
        self.stack.addWidget(self.history_page)
        self.stack.setCurrentIndex(0)

    def connect_signals(self):
        self.dashboard_btn.clicked.connect(lambda: self.switch_page(0))
        self.analytics_btn.clicked.connect(lambda: self.switch_page(1))
        self.history_btn.clicked.connect(lambda: self.switch_page(2))
        self.logout_button.clicked.connect(self.confirm_exit)
        self.theme_button.clicked.connect(self.toggle_theme)

        self.ukr_button.clicked.connect(lambda: self.change_language("uk"))
        self.eng_button.clicked.connect(lambda: self.change_language("en"))

    def change_language(self, language):
        if language == self.current_language:
            self.update_language_buttons()
            return

        self.current_language = language
        self.update_language()
        self.update_language_buttons()

    def update_language_buttons(self):
        self.ukr_button.setChecked(self.current_language == "uk")
        self.eng_button.setChecked(self.current_language == "en")

        for button in [self.ukr_button, self.eng_button]:
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

    def update_language(self):
        self.setWindowTitle(self.tr("window_title"))

        self.language_title.setText(self.tr("language"))
        self.theme_title.setText(self.tr("theme"))
        self.menu_title.setText(self.tr("menu"))

        self.dashboard_btn.setText(f"🏠 {self.tr('dashboard')}")
        self.analytics_btn.setText(f"📊 {self.tr('analysis')}")
        self.history_btn.setText(f"🕘 {self.tr('history')}")
        self.logout_button.setText(f"🚪 {self.tr('exit')}")

        if hasattr(self, "dashboard_page"):
            self.dashboard_page.update_language()

        if hasattr(self, "analysis_page"):
            self.analysis_page.update_language()

        if hasattr(self, "history_page"):
            self.history_page.update_language()

        self.update_language_buttons()
        self.update_theme_button()

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_styles()

        if hasattr(self, "analysis_page") and hasattr(self.analysis_page, "risk_gauge"):
            self.analysis_page.risk_gauge.set_theme(self.current_theme)

        if hasattr(self, "analysis_page") and hasattr(self.analysis_page, "analysis_plot"):
            self.analysis_page.analysis_plot.set_theme(self.current_theme)

        self.update_theme_button()

    def update_theme_button(self):
        if self.current_theme == "dark":
            self.theme_button.setText("☀️ Light")
        else:
            self.theme_button.setText("🌙 Dark")

        self.theme_button.style().unpolish(self.theme_button)
        self.theme_button.style().polish(self.theme_button)
        self.theme_button.update()

    def confirm_exit(self):
        msg_box = QMessageBox(self)
        msg_box.setObjectName("exitMessageBox")
        msg_box.setWindowTitle(self.tr("exit_title"))
        msg_box.setText(self.tr("exit_text"))
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        msg_box.button(QMessageBox.Yes).setText(self.tr("yes"))
        msg_box.button(QMessageBox.No).setText(self.tr("no"))

        if msg_box.exec() == QMessageBox.Yes:
            self.close()

    def update_active_button(self, index):
        buttons = [
            self.dashboard_btn,
            self.analytics_btn,
            self.history_btn
        ]

        for button in buttons:
            button.setProperty("active", False)

        buttons[index].setProperty("active", True)

        for button in buttons:
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        self.update_active_button(index)

    def apply_styles(self):
        try:
            if self.current_theme == "light":
                style_path = "styles/light.qss"
            else:
                style_path = "styles/main.qss"

            with open(style_path, "r", encoding="utf-8") as file:
                self.setStyleSheet(file.read())

        except Exception as e:
            print("Помилка завантаження стилів:", e)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.showNormal()
        else:
            super().keyPressEvent(event)