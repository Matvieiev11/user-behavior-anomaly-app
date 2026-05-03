from PySide6.QtWidgets import QApplication
import sys

from ui.windows.login_window import LoginWindow
from utils.database import init_database

def main():
    app = QApplication(sys.argv)
    init_database()
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()