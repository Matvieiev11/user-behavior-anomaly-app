from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
)

from utils.database import get_connection


class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def tr(self, key):
        if hasattr(self, "main_window"):
            return self.main_window.tr(key)
        return key

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)
        self.setLayout(layout)

        top_layout = QHBoxLayout()

        self.title_label = QLabel()
        self.title_label.setObjectName("mainTitle")

        top_layout.addWidget(self.title_label)
        top_layout.addStretch()

        self.refresh_button = QPushButton()
        self.refresh_button.setObjectName("primaryButton")
        top_layout.addWidget(self.refresh_button)

        layout.addLayout(top_layout)

        table_frame = QFrame()
        table_frame.setObjectName("sectionFrame")

        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(16, 16, 16, 16)
        table_layout.setSpacing(10)

        self.table_title = QLabel()
        self.table_title.setObjectName("sectionTitle")

        self.history_table = QTableWidget()
        self.history_table.setMinimumHeight(650)

        table_layout.addWidget(self.table_title)
        table_layout.addWidget(self.history_table)

        table_frame.setLayout(table_layout)
        layout.addWidget(table_frame)

        self.refresh_button.clicked.connect(self.load_history)

    def update_language(self):
        self.title_label.setText(self.tr("history_page_title"))
        self.refresh_button.setText(self.tr("refresh"))
        self.table_title.setText(self.tr("analysis_history"))
        self.load_history()

    def load_history(self):
        headers = [
            "ID",
            self.tr("user"),
            "Email",
            self.tr("date_time"),
            self.tr("file"),
            self.tr("sessions_count_short"),
            self.tr("anomalies_count")
        ]

        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT
                    id,
                    username,
                    email,
                    datetime,
                    file_name,
                    sessions_count,
                    anomalies_count
                FROM analysis_history
                ORDER BY id DESC
            """)
            rows = cursor.fetchall()

        self.history_table.setRowCount(len(rows))
        self.history_table.setColumnCount(len(headers))
        self.history_table.setHorizontalHeaderLabels(headers)

        for row_index, row_data in enumerate(rows):
            for col_index, value in enumerate(row_data):
                self.history_table.setItem(
                    row_index,
                    col_index,
                    QTableWidgetItem(str(value))
                )

        self.history_table.resizeColumnsToContents()