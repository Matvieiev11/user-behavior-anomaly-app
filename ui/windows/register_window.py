from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame
)

from services.auth_service import register_user


class RegisterWindow(QWidget):
    def __init__(self, login_window=None):
        super().__init__()
        self.login_window = login_window

        self.setWindowTitle("Register")
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

        self.title_label = QLabel("Create Account")
        self.title_label.setObjectName("mainTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 22px; font-weight: 700;")

        self.subtitle_label = QLabel("Register with your email")
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

        self.register_button = QPushButton("Register")
        self.register_button.setObjectName("primaryButton")
        self.register_button.setMinimumHeight(46)

        self.back_button = QPushButton("Back to Login")
        self.back_button.setObjectName("secondaryButton")
        self.back_button.setMinimumHeight(46)

        form_layout.addWidget(self.title_label)
        form_layout.addWidget(self.subtitle_label)
        form_layout.addSpacing(8)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.password_input)
        form_layout.addSpacing(8)
        form_layout.addWidget(self.register_button)
        form_layout.addWidget(self.back_button)

        self.form_frame.setLayout(form_layout)
        outer_layout.addWidget(self.form_frame)

        self.register_button.clicked.connect(self.handle_register)
        self.back_button.clicked.connect(self.go_back)

    def apply_styles(self):
        try:
            with open("styles/main.qss", "r", encoding="utf-8") as file:
                self.setStyleSheet(file.read())
        except Exception as e:
            print("Style loading error:", e)

    def handle_register(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        success, result = register_user(email, password)

        if success:
            self.show_message(
                "Success",
                f"Account created successfully.\nUsername: {result['username']}",
                QMessageBox.Information
            )
        else:
            self.show_message("Registration Error", result, QMessageBox.Warning)

    def show_message(self, title, text, icon=QMessageBox.Information):
        msg_box = QMessageBox(self)
        msg_box.setObjectName("authMessageBox")
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.button(QMessageBox.Ok).setText("OK")
        msg_box.exec()

    def go_back(self):
        if self.login_window is not None:
            self.login_window.show()
        self.close()