from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout,
    QComboBox, QGridLayout, QScrollArea
)
from services.risk_service import calculate_user_risk_score
from plots.plotter import ActivityPlotCanvas
from ui.widgets.stat_card import StatCard
from ui.widgets.risk_gauge import RiskGauge
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar


class AnalysisPage(QWidget):
    def __init__(self):
        super().__init__()
        self.data = None
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
        scroll.setObjectName("analysisScrollArea")
        outer_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)
        container.setLayout(layout)

        self.title_label = QLabel()
        self.title_label.setObjectName("mainTitle")
        layout.addWidget(self.title_label)

        top_frame = QFrame()
        top_frame.setObjectName("sectionFrame")

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(16, 16, 16, 16)
        top_layout.setSpacing(12)

        self.user_label = QLabel()
        self.user_label.setObjectName("filterLabel")

        self.analysis_user_combo = QComboBox()
        self.analysis_user_combo.setObjectName("darkCombo")

        self.analysis_status = QLabel()
        self.analysis_status.setObjectName("statusLabel")

        top_layout.addWidget(self.user_label)
        top_layout.addWidget(self.analysis_user_combo, 1)
        top_layout.addWidget(self.analysis_status, 2)

        top_frame.setLayout(top_layout)
        layout.addWidget(top_frame)

        indicators_layout = QHBoxLayout()
        indicators_layout.setSpacing(16)

        gauge_container = QFrame()
        gauge_container.setObjectName("sectionFrame")

        gauge_layout = QVBoxLayout()
        gauge_layout.setContentsMargins(10, 10, 10, 10)
        gauge_layout.setSpacing(6)

        self.risk_gauge = RiskGauge()
        self.risk_gauge.setMinimumHeight(200)

        self.gauge_label = QLabel()
        self.gauge_label.setAlignment(Qt.AlignCenter)
        self.gauge_label.setObjectName("gaugeSubLabel")

        gauge_layout.addWidget(self.risk_gauge)
        gauge_layout.addWidget(self.gauge_label)
        gauge_container.setLayout(gauge_layout)

        self.insights_frame = QFrame()
        self.insights_frame.setObjectName("sectionFrame")
        self.insights_frame.setMinimumHeight(220)

        insights_layout = QVBoxLayout()
        insights_layout.setContentsMargins(18, 18, 18, 18)
        insights_layout.setSpacing(10)

        self.insights_title = QLabel()
        self.insights_title.setObjectName("sectionTitle")

        self.insights_content = QLabel()
        self.insights_content.setObjectName("insightsText")
        self.insights_content.setWordWrap(True)
        self.insights_content.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        insights_layout.addWidget(self.insights_title)
        insights_layout.addWidget(self.insights_content)
        insights_layout.addStretch()

        self.insights_frame.setLayout(insights_layout)

        indicators_layout.addWidget(gauge_container)
        indicators_layout.addWidget(self.insights_frame)

        layout.addLayout(indicators_layout)

        cards_layout = QGridLayout()
        cards_layout.setSpacing(16)

        self.analysis_card_count = StatCard("", "0")
        self.analysis_card_ip = StatCard("", "0")
        self.analysis_card_time = StatCard("", "-")
        self.analysis_card_device = StatCard("", "0")
        self.analysis_card_location = StatCard("", "0")
        self.analysis_card_actions_dev = StatCard("", "0")
        self.analysis_card_duration_dev = StatCard("", "0")
        self.analysis_card_max_dev = StatCard("", "-")

        cards_layout.addWidget(self.analysis_card_count, 0, 0)
        cards_layout.addWidget(self.analysis_card_ip, 0, 1)
        cards_layout.addWidget(self.analysis_card_device, 0, 2)
        cards_layout.addWidget(self.analysis_card_location, 0, 3)
        cards_layout.addWidget(self.analysis_card_actions_dev, 1, 0)
        cards_layout.addWidget(self.analysis_card_duration_dev, 1, 1)
        cards_layout.addWidget(self.analysis_card_time, 1, 2)
        cards_layout.addWidget(self.analysis_card_max_dev, 1, 3)

        layout.addLayout(cards_layout)

        graph_frame = QFrame()
        graph_frame.setObjectName("sectionFrame")

        graph_layout = QVBoxLayout()
        graph_layout.setContentsMargins(16, 16, 16, 16)
        graph_layout.setSpacing(12)

        self.graph_selector = QComboBox()
        self.graph_selector.setObjectName("darkCombo")
        graph_layout.addWidget(self.graph_selector)

        self.analysis_plot = ActivityPlotCanvas(self)
        self.analysis_plot.clear_plot()
        self.analysis_plot.setMinimumHeight(560)

        self.plot_toolbar = NavigationToolbar(self.analysis_plot, self)
        self.plot_toolbar.setObjectName("plotToolbar")

        graph_layout.addWidget(self.plot_toolbar)
        graph_layout.addWidget(self.analysis_plot)

        graph_frame.setLayout(graph_layout)
        layout.addWidget(graph_frame)

        self.analysis_user_combo.currentIndexChanged.connect(self.update_analysis)
        self.graph_selector.currentIndexChanged.connect(self.update_analysis)

    def update_language(self):
        self.title_label.setText(self.tr("analysis_page_title"))
        self.user_label.setText(self.tr("user_label"))
        self.gauge_label.setText(self.tr("integral_risk_score"))
        self.insights_title.setText(self.tr("risk_reasons"))

        self.analysis_card_count.title_label.setText(self.tr("anomalous_sessions"))
        self.analysis_card_time.title_label.setText(self.tr("typical_login_time"))
        self.analysis_card_device.title_label.setText(self.tr("device_changes"))
        self.analysis_card_location.title_label.setText(self.tr("location_changes"))
        self.analysis_card_ip.title_label.setText(self.tr("ip_changes"))
        self.analysis_card_actions_dev.title_label.setText(self.tr("typical_activity"))
        self.analysis_card_duration_dev.title_label.setText(self.tr("typical_duration"))
        self.analysis_card_max_dev.title_label.setText(self.tr("max_deviation"))

        current_user_id = self.analysis_user_combo.currentData()

        self.analysis_user_combo.blockSignals(True)
        self.analysis_user_combo.clear()
        self.analysis_user_combo.addItem(self.tr("select_user"), None)

        if self.data is not None:
            users = self.data[["user_id", "username"]].drop_duplicates()
            for _, row in users.iterrows():
                display = f"{row['username']} (ID: {row['user_id']})"
                self.analysis_user_combo.addItem(display, row["user_id"])

            if current_user_id is not None:
                for i in range(self.analysis_user_combo.count()):
                    if self.analysis_user_combo.itemData(i) == current_user_id:
                        self.analysis_user_combo.setCurrentIndex(i)
                        break

        self.analysis_user_combo.blockSignals(False)

        current_graph = self.graph_selector.currentData() if self.graph_selector.count() > 0 else None

        self.graph_selector.blockSignals(True)
        self.graph_selector.clear()
        self.graph_selector.addItem(self.tr("activity_chart"), "activity")
        self.graph_selector.addItem(self.tr("failed_attempts_chart"), "failed_attempts")
        self.graph_selector.addItem(self.tr("session_duration_chart"), "session_duration")
        self.graph_selector.addItem(self.tr("anomaly_distribution_chart"), "anomaly_distribution")
        self.graph_selector.addItem(self.tr("deviation_chart"), "deviations")

        if current_graph is not None:
            for i in range(self.graph_selector.count()):
                if self.graph_selector.itemData(i) == current_graph:
                    self.graph_selector.setCurrentIndex(i)
                    break
        self.graph_selector.blockSignals(False)

        if self.data is None:
            self.analysis_status.setText(self.tr("select_user_for_analysis"))
            self.insights_content.setText(self.tr("select_user_for_analysis"))
        else:
            self.update_analysis()

    def set_data(self, data):
        self.data = data
        self.update_language()

        if data is None:
            self.analysis_status.setText(self.tr("data_not_transferred"))
            self.reset_analysis_view()
            return

        self.analysis_status.setText(self.tr("data_transferred_select_user"))
        self.reset_analysis_view()

    def reset_analysis_view(self):
        self.analysis_card_count.set_value("0")
        self.analysis_card_time.set_value("-")
        self.analysis_card_ip.set_value("0")
        self.analysis_card_device.set_value("0")
        self.analysis_card_location.set_value("0")
        self.analysis_card_actions_dev.set_value("-")
        self.analysis_card_duration_dev.set_value("-")
        self.analysis_card_max_dev.set_value("-")

        self.risk_gauge.set_value(0)
        self.insights_content.setText(self.tr("select_user_for_analysis"))
        self.analysis_plot.clear_plot()

    def update_analysis(self):
        if self.data is None:
            self.analysis_status.setText(self.tr("data_not_loaded"))
            self.insights_content.setText(self.tr("run_analysis_on_dashboard_first"))
            self.reset_analysis_view()
            return

        user_id = self.analysis_user_combo.currentData()

        if user_id is None:
            self.analysis_status.setText(self.tr("select_user_for_analysis"))
            self.reset_analysis_view()
            return

        user_data = self.data[self.data["user_id"] == user_id]

        if user_data.empty:
            self.analysis_status.setText(f"{self.tr('no_data_for_user')} {user_id}")
            self.reset_analysis_view()
            self.insights_content.setText(self.tr("selected_user_data_missing"))
            return

        total_sessions = len(user_data)
        anomalies_count = len(user_data[user_data["anomaly"] == -1])

        # Базові метрики для карток та insights
        typical_time = round(float(user_data["login_hour"].median()), 2)

        behavior_outliers = (
            int(user_data["behavior_outlier"].sum())
            if "behavior_outlier" in user_data.columns
            else 0
        )

        device_changes = int(user_data["device_changed"].sum()) if "device_changed" in user_data.columns else 0
        location_changes = int(user_data["location_changed"].sum()) if "location_changed" in user_data.columns else 0
        ip_changes = int(user_data["ip_changed"].sum()) if "ip_changed" in user_data.columns else 0

        avg_login_dev = float(user_data["login_hour_dev"].mean())
        avg_actions_dev = float(user_data["actions_dev"].mean())
        avg_duration_dev = float(user_data["duration_dev"].mean())
        avg_failed_dev = (
            float(user_data["failed_dev"].mean())
            if "failed_dev" in user_data.columns
            else float(user_data["failed_attempts"].mean())
        )
        typical_actions = round(float(user_data["actions_count"].median()), 2)
        typical_duration = round(float(user_data["session_duration"].median()), 2)

        # Найбільше реальне відхилення
        max_dev = max([
            (self.tr("activity_short"), float(user_data["actions_dev"].max())),
            (self.tr("login_time_short"), float(user_data["login_hour_dev"].max())),
            (self.tr("duration_short"), float(user_data["duration_dev"].max()))
        ], key=lambda x: x[1])

        self.analysis_card_max_dev.set_value(f"{max_dev[0]} (+{max_dev[1]:.1f})")

        risk_score = calculate_user_risk_score(user_data)

        # Оновлення карток
        self.analysis_card_count.set_value(anomalies_count)
        self.analysis_card_time.set_value(typical_time)
        self.analysis_card_ip.set_value(ip_changes)
        self.analysis_card_device.set_value(device_changes)
        self.analysis_card_location.set_value(location_changes)
        self.analysis_card_actions_dev.set_value(typical_actions)
        self.analysis_card_duration_dev.set_value(typical_duration)

        # Gauge + статус
        self.risk_gauge.set_value(risk_score)
        selected_text = self.analysis_user_combo.currentText()
        self.analysis_status.setText(f"{self.tr('analysis_for_user')} {selected_text}")

        # Insights
        insights = []

        if anomalies_count > 0:
            insights.append(self.tr("insight_model_anomalies_detected"))
        else:
            insights.append(self.tr("no_model_anomalies_detected"))

        if behavior_outliers > 0:
            insights.append(self.tr("insight_behavior_outliers_detected"))

        if avg_login_dev > 3:
            insights.append(self.tr("insight_login_deviation"))

        if avg_actions_dev > 10:
            insights.append(self.tr("insight_activity_deviation"))

        if avg_duration_dev > 8:
            insights.append(self.tr("insight_duration_deviation"))

        if avg_failed_dev > 1:
            insights.append(self.tr("insight_failed_attempts"))

        if anomalies_count > 0:
            if ip_changes > 0:
                insights.append(self.tr("insight_ip_change"))

            if device_changes > 0:
                insights.append(self.tr("insight_device_change"))

            if location_changes > 0:
                insights.append(self.tr("insight_location_change"))
        else:
            if ip_changes > 0 or device_changes > 0 or location_changes > 0:
                insights.append(self.tr("insight_context_changes_without_anomaly"))

        if not insights:
            insights.append(self.tr("behavior_within_normal_range"))

        self.insights_content.setText("\n\n".join(insights))

        # Графік
        selected_graph = self.graph_selector.currentData()

        if selected_graph == "activity":
            self.analysis_plot.plot_user_activity(self.data, user_id)
        elif selected_graph == "failed_attempts":
            self.analysis_plot.plot_failed_attempts(self.data, user_id)
        elif selected_graph == "session_duration":
            self.analysis_plot.plot_session_duration(self.data, user_id)
        elif selected_graph == "anomaly_distribution":
            self.analysis_plot.plot_anomaly_distribution(self.data, user_id)
        elif selected_graph == "deviations":
            self.analysis_plot.plot_deviations(self.data, user_id)