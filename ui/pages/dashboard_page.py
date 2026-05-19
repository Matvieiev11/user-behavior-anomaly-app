from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog,
    QTableWidget, QTableWidgetItem, QComboBox, QHBoxLayout, QFrame,
    QGridLayout, QSizePolicy, QScrollArea
)
from utils.data_loader import load_data
from models.anomaly_detector import detect_anomalies
from utils.statistics import get_user_statistics
from utils.exporter import export_to_csv
from ui.widgets.stat_card import StatCard
from services.history_service import log_analysis
from services.report_service import generate_pdf_report
from services.email_service import send_email_report
from services.risk_service import calculate_user_risk_score
from time import perf_counter
from services.compare_approaches import print_detection_approaches_comparison

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()

        self.file_path = None
        self.data = None
        self.result_data = None
        self.current_display_data = None
        self.user_stats = {}
        self.last_sessions_count = 0
        self.last_anomalies_count = 0
        self.setup_ui()

    def tr(self, key):
        if hasattr(self, "main_window"):
            return self.main_window.tr(key)
        return key

    def setup_ui(self):
        outer_layout = QVBoxLayout()
        self.setLayout(outer_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("dashboardScrollArea")
        outer_layout.addWidget(scroll)
        container = QWidget()
        scroll.setWidget(container)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)
        container.setLayout(layout)

        # Верхня панель
        top_bar = QHBoxLayout()

        title_block = QVBoxLayout()
        self.title_label = QLabel()
        self.title_label.setObjectName("mainTitle")

        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("subTitle")

        title_block.addWidget(self.title_label)
        title_block.addWidget(self.subtitle_label)

        top_bar.addLayout(title_block)
        top_bar.addStretch()

        self.export_button = QPushButton()
        self.export_button.setObjectName("primaryButton")
        top_bar.addWidget(self.export_button)

        self.email_report_button = QPushButton()
        self.email_report_button.setObjectName("primaryButton")
        top_bar.addWidget(self.email_report_button)

        layout.addLayout(top_bar)

        # Панель керування
        controls_frame = QFrame()
        controls_frame.setObjectName("sectionFrame")

        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(16, 16, 16, 16)
        controls_layout.setSpacing(12)

        self.file_label = QLabel()
        self.file_label.setObjectName("infoLabel")
        self.file_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.load_button = QPushButton()
        self.load_button.setObjectName("accentButton")

        self.analyze_button = QPushButton()
        self.analyze_button.setObjectName("accentButton")

        self.show_anomalies_button = QPushButton()
        self.show_anomalies_button.setObjectName("secondaryButton")

        self.show_all_button = QPushButton()
        self.show_all_button.setObjectName("secondaryButton")

        controls_layout.addWidget(self.file_label, 2)
        controls_layout.addWidget(self.load_button)
        controls_layout.addWidget(self.analyze_button)
        controls_layout.addWidget(self.show_anomalies_button)
        controls_layout.addWidget(self.show_all_button)

        controls_frame.setLayout(controls_layout)
        layout.addWidget(controls_frame)

        # Картки
        cards_layout = QGridLayout()
        cards_layout.setSpacing(16)

        self.card_anomalies = StatCard("", "0")
        self.card_users = StatCard("", "0")
        self.card_sessions = StatCard("", "0")
        self.card_system_risk = StatCard("", "0")

        cards_layout.addWidget(self.card_anomalies, 0, 0)
        cards_layout.addWidget(self.card_users, 0, 1)
        cards_layout.addWidget(self.card_sessions, 0, 2)
        cards_layout.addWidget(self.card_system_risk, 0, 3)

        layout.addLayout(cards_layout)

        # Фільтр користувача
        filter_frame = QFrame()
        filter_frame.setObjectName("sectionFrame")

        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(16, 16, 16, 16)
        filter_layout.setSpacing(12)

        self.user_select_label = QLabel()
        self.user_select_label.setObjectName("filterLabel")

        self.user_combo = QComboBox()
        self.user_combo.setObjectName("darkCombo")

        self.result_label = QLabel()
        self.result_label.setObjectName("statusLabel")

        filter_layout.addWidget(self.user_select_label)
        filter_layout.addWidget(self.user_combo, 1)
        filter_layout.addWidget(self.result_label, 2)

        filter_frame.setLayout(filter_layout)
        layout.addWidget(filter_frame)

        # Статистика
        self.stats_label = QLabel()
        self.stats_label.setObjectName("statsLabel")
        layout.addWidget(self.stats_label)

        # Таблиця
        table_frame = QFrame()
        table_frame.setObjectName("sectionFrame")

        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(16, 16, 16, 16)
        table_layout.setSpacing(10)

        self.table_title = QLabel()
        self.table_title.setObjectName("sectionTitle")
        self.table = QTableWidget()
        self.table.setMinimumHeight(600)

        table_layout.addWidget(self.table_title)
        table_layout.addWidget(self.table)
        table_frame.setLayout(table_layout)
        layout.addWidget(table_frame)
        layout.addStretch()

        # Сигнали
        self.load_button.clicked.connect(self.load_file)
        self.analyze_button.clicked.connect(self.analyze_data)
        self.show_anomalies_button.clicked.connect(self.show_only_anomalies)
        self.show_all_button.clicked.connect(self.show_all_data)
        self.export_button.clicked.connect(self.export_results)
        self.user_combo.currentIndexChanged.connect(self.show_selected_user_stats)
        self.email_report_button.clicked.connect(self.send_report_to_email)

    def update_language(self):
        self.title_label.setText(self.tr("dashboard_page_title"))

        self.export_button.setText(self.tr("export_csv"))
        self.email_report_button.setText(self.tr("send_email_report"))
        self.load_button.setText(self.tr("load_data"))
        self.analyze_button.setText(self.tr("run_analysis"))
        self.show_anomalies_button.setText(self.tr("show_anomalies_only"))
        self.show_all_button.setText(self.tr("show_all_records"))

        self.card_anomalies.title_label.setText(self.tr("found_anomalies"))
        self.card_users.title_label.setText(self.tr("users_count"))
        self.card_sessions.title_label.setText(self.tr("sessions_count"))
        self.card_system_risk.title_label.setText(self.tr("system_risk_level"))

        self.user_select_label.setText(self.tr("select_user"))
        self.table_title.setText(self.tr("events_and_results"))

        if self.file_path:
            self.file_label.setText(f"{self.tr('selected_file')}: {self.file_path}")
        else:
            self.file_label.setText(self.tr("file_not_selected"))

        if self.result_data is None:
            self.result_label.setText(self.tr("analysis_result_empty"))
            self.stats_label.setText(self.tr("user_stats_unavailable"))
            self.user_combo.clear()
            self.user_combo.addItem(self.tr("user_not_selected"))
        else:
            self.fill_user_combo()
            self.show_selected_user_stats()

    def reset_dashboard_view(self):
        self.card_anomalies.set_value("0")
        self.card_users.set_value("0")
        self.card_sessions.set_value("0")
        self.card_system_risk.set_value("-")

        self.result_label.setText(self.tr("analysis_result_empty"))
        self.stats_label.setText(self.tr("user_stats_unavailable"))

        self.user_combo.clear()
        self.user_combo.addItem(self.tr("user_not_selected"))

    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("select_csv_file"),
            "",
            "CSV Files (*.csv)"
        )

        if file_name:
            self.file_path = file_name
            self.file_label.setText(f"{self.tr('selected_file')}: {file_name}")
            self.result_label.setText(self.tr("file_loaded_ready"))

    def analyze_data(self):
        if not self.file_path:
            self.result_label.setText(self.tr("select_csv_first"))
            return

        total_start_time = perf_counter()

        file_load_start_time = perf_counter()
        self.data = load_data(self.file_path)
        file_load_time = perf_counter() - file_load_start_time

        if self.data is None:
            self.result_label.setText(self.tr("data_load_error"))
            return

        analysis_start_time = perf_counter()
        self.result_data = detect_anomalies(self.data)
        analysis_time = perf_counter() - analysis_start_time

        total_time = perf_counter() - total_start_time

        self.user_stats = get_user_statistics(self.result_data)

        anomalies_count = len(self.result_data[self.result_data["anomaly"] == -1])
        users_count = len(self.result_data["user_id"].unique())
        sessions_count = len(self.result_data)
        system_risk = round((anomalies_count / sessions_count) * 100, 1) if sessions_count else 0

        if system_risk < 10:
            risk_color = "#22c55e"
        elif system_risk < 25:
            risk_color = "#f59e0b"
        else:
            risk_color = "#ef4444"

        print("=== Результати експериментального запуску ===")
        print(f"Проаналізовано сеансів: {sessions_count}")
        print(f"Кількість користувачів: {users_count}")
        print(f"Виявлено аномалій: {anomalies_count}")
        print(f"Загальний системний ризик: {system_risk:.2f}%")
        print(f"Час зчитування CSV-файлу: {file_load_time:.3f} с")
        print(f"Час виконання аналізу: {analysis_time:.3f} с")
        print(f"Загальний час виконання: {total_time:.3f} с")

        print_detection_approaches_comparison(self.data)

        self.last_sessions_count = sessions_count
        self.last_anomalies_count = anomalies_count
        current_user = None
        if hasattr(self, "main_window"):
            current_user = getattr(self.main_window, "current_user", None)

        log_analysis(
            current_user,
            self.file_path,
            sessions_count,
            anomalies_count
        )

        self.card_anomalies.set_value(anomalies_count)
        self.card_users.set_value(users_count)
        self.card_sessions.set_value(sessions_count)
        self.card_system_risk.set_value_with_color(f"{system_risk}%", risk_color)

        self.result_label.setText(
            f"{self.tr('analysis_complete_found')}: {anomalies_count}"
        )

        self.show_table(self.result_data)
        self.fill_user_combo()
        self.stats_label.setText(self.tr("user_stats_unavailable"))

        if hasattr(self, "main_window"):
            self.main_window.analysis_page.set_data(self.result_data)

    def send_report_to_email(self):
        if self.result_data is None:
            self.result_label.setText(self.tr("run_analysis_first"))
            return

        user_id = self.get_selected_user_id()

        if user_id is None:
            self.result_label.setText(self.tr("select_user_for_pdf_report"))
            return

        current_user = getattr(self.main_window, "current_user", None) if hasattr(self, "main_window") else None
        current_language = getattr(self.main_window, "current_language", "uk") if hasattr(self, "main_window") else "uk"

        if not current_user or not current_user.get("email"):
            self.result_label.setText(self.tr("no_logged_user_email"))
            return

        user_data = self.result_data[self.result_data["user_id"] == user_id]

        if user_data.empty:
            self.result_label.setText(self.tr("selected_user_data_missing"))
            return

        risk_score = calculate_user_risk_score(user_data)

        pdf_path = generate_pdf_report(user=current_user, analyzed_user_data=user_data, file_path=self.file_path,
                                       risk_score=risk_score, language=current_language)

        success, message = send_email_report(
            current_user["email"],
            pdf_path,
            current_language
        )

        if success:
            self.result_label.setText(
                f"{self.tr('email_sent_success')}: {current_user['email']}"
            )
        else:
            self.result_label.setText(
                f"{self.tr('email_sent_error')}: {message}"
            )
    def show_table(self, data):
        self.current_display_data = data.copy()

        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data.columns))
        self.table.setHorizontalHeaderLabels(data.columns)
        self.table.setAlternatingRowColors(True)

        for row in range(len(data)):
            is_anomaly = "anomaly" in data.columns and str(data.iloc[row]["anomaly"]) == "-1"

            for col in range(len(data.columns)):
                value = str(data.iat[row, col])
                item = QTableWidgetItem(value)

                if is_anomaly:
                    item.setBackground(QColor(255, 200, 200))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    item.setForeground(QColor(40, 40, 40))

                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()

    def fill_user_combo(self):
        self.user_combo.clear()
        self.user_combo.addItem(self.tr("user_not_selected"))

        if self.result_data is None:
            return

        users = self.result_data[["user_id", "username"]].drop_duplicates()

        for _, row in users.iterrows():
            display = f"{row['username']} (ID: {row['user_id']})"
            self.user_combo.addItem(display, row["user_id"])

    def get_selected_user_id(self):
        return self.user_combo.currentData()

    def get_username_by_user_id(self, user_id):
        if self.result_data is None or user_id is None:
            return None

        user_rows = self.result_data[self.result_data["user_id"] == user_id]
        if user_rows.empty:
            return None

        return user_rows.iloc[0]["username"]

    def show_selected_user_stats(self):
        user_id = self.get_selected_user_id()

        if user_id is None:
            self.stats_label.setText(self.tr("user_stats_unavailable"))

            if self.result_data is not None:
                self.show_table(self.result_data)
            return

        if user_id not in self.user_stats:
            return

        stats = self.user_stats[user_id]
        username = self.get_username_by_user_id(user_id)

        text = (
            f"{self.tr('user')}: {username} | "
            f"{self.tr('sessions_count_short')}: {stats['total_sessions']} | "
            f"{self.tr('avg_duration')}: {stats['avg_duration']} | "
            f"{self.tr('avg_actions')}: {stats['avg_actions']} | "
            f"{self.tr('avg_login_hour')}: {stats['avg_login_hour']} | "
            f"{self.tr('anomalies_count')}: {stats['anomalies_count']}"
        )

        self.stats_label.setText(text)
        filtered_data = self.result_data[self.result_data["user_id"] == user_id]
        self.show_table(filtered_data)

    def show_only_anomalies(self):
        if self.result_data is None:
            self.result_label.setText(self.tr("run_analysis_first"))
            return

        user_id = self.get_selected_user_id()

        if user_id is None:
            anomalies_data = self.result_data[self.result_data["anomaly"] == -1]
            self.show_table(anomalies_data)
            self.result_label.setText(
                f"{self.tr('showing_all_anomalies')}: {len(anomalies_data)}"
            )
            return

        anomalies_data = self.result_data[
            (self.result_data["user_id"] == user_id) &
            (self.result_data["anomaly"] == -1)
        ]
        self.show_table(anomalies_data)

        username = self.get_username_by_user_id(user_id)
        self.result_label.setText(
            f"{self.tr('showing_user_anomalies')} {username}. {self.tr('count')}: {len(anomalies_data)}"
        )

    def show_all_data(self):
        if self.result_data is None:
            self.result_label.setText(self.tr("run_analysis_first"))
            return

        user_id = self.get_selected_user_id()

        if user_id is None:
            self.show_table(self.result_data)
            self.result_label.setText(self.tr("showing_all_records"))
            return

        filtered_data = self.result_data[self.result_data["user_id"] == user_id]
        self.show_table(filtered_data)

        username = self.get_username_by_user_id(user_id)
        self.result_label.setText(f"{self.tr('showing_user_records')} {username}.")

    def export_results(self):
        if self.current_display_data is None or self.current_display_data.empty:
            self.result_label.setText(self.tr("no_data_to_export"))
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("save_results"),
            "results.csv",
            "CSV Files (*.csv)"
        )

        if not file_name:
            return

        success = export_to_csv(self.current_display_data, file_name)

        if success:
            self.result_label.setText(f"{self.tr('export_success')}: {file_name}")
        else:
            self.result_label.setText(self.tr("export_error"))