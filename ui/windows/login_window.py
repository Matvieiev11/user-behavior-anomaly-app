from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame
)

from services.auth_service import login_user
from ui.windows.register_window import RegisterWindow
from ui.windows.main_window import MainWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.register_window = None
        self.main_window = None

        self.setWindowTitle("Login")
        self.setFixedSize(480, 420)
        self.setObjectName("authWindow")

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(28, 28, 28, 28)
        self.setLayout(outer_layout)

        self.form_frame = QFrame()
        self.form_frame.setObjectName("sectionFrame")

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(18)

        self.title_label = QLabel("User Behavior Analysis")
        self.title_label.setObjectName("mainTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 22px; font-weight: 700;")

        self.subtitle_label = QLabel("Login to continue")
        self.subtitle_label.setObjectName("subTitle")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet("font-size: 14px; color: #94a3b8;")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setObjectName("authInput")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("authInput")

        self.login_button = QPushButton("Login")
        self.login_button.setObjectName("primaryButton")
        self.login_button.setMinimumHeight(46)

        self.register_button = QPushButton("Create Account")
        self.register_button.setObjectName("secondaryButton")
        self.register_button.setMinimumHeight(46)

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
        outer_layout.addWidget(self.form_frame)
        outer_layout.addStretch()
        self.form_frame.setMaximumWidth(420)

        self.login_button.clicked.connect(self.handle_login)
        self.register_button.clicked.connect(self.open_register)

    def apply_styles(self):
        try:
            with open("styles/main.qss", "r", encoding="utf-8") as file:
                self.setStyleSheet(file.read())
        except Exception as e:
            print("Style loading error:", e)

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        success, result = login_user(email, password)

        if success:
            self.main_window = MainWindow()
            self.main_window.current_user = result
            self.main_window.show()
            self.close()
        else:
            self.show_message("Login Error", result, QMessageBox.Warning)

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
        self.register_window.show()
        self.hide()