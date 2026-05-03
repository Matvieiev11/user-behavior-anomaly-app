from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ActivityPlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.figure = Figure(facecolor="#111827")
        self.ax = self.figure.add_subplot(111)
        super().__init__(self.figure)

        self.current_theme = "dark"

        self._hover_annotation = None
        self._hover_points = []
        self._hover_data = []

        self.apply_plot_theme()
        self.create_hover_annotation()

        self.mpl_connect("motion_notify_event", self.on_hover)

    def tr(self, key):
        parent = self.parent()

        while parent is not None:
            if hasattr(parent, "main_window") and parent.main_window is not None:
                return parent.main_window.tr(key)
            parent = parent.parent()

        return key

    def get_main_window(self):
        parent = self.parent()

        while parent is not None:
            if hasattr(parent, "main_window") and parent.main_window is not None:
                return parent.main_window
            parent = parent.parent()

        return None

    def get_current_theme(self):
        main_window = self.get_main_window()

        if main_window is not None:
            return getattr(main_window, "current_theme", self.current_theme)

        return self.current_theme

    def set_theme(self, theme):
        self.current_theme = theme
        self.apply_plot_theme()

        if self._hover_annotation is not None:
            colors = self.get_theme_colors()

            self._hover_annotation.get_bbox_patch().set_facecolor(colors["annotation_bg"])
            self._hover_annotation.get_bbox_patch().set_edgecolor(colors["annotation_edge"])
            self._hover_annotation.set_color(colors["annotation_text"])

        self.draw_idle()

    def get_theme_colors(self):
        theme = self.get_current_theme()

        if theme == "light":
            return {
                "figure_bg": "#ffffff",
                "axes_bg": "#ffffff",
                "text": "#0f172a",
                "label": "#334155",
                "grid": "#cbd5e1",
                "spine": "#94a3b8",
                "legend_bg": "#ffffff",
                "legend_edge": "#cbd5e1",
                "annotation_bg": "#ffffff",
                "annotation_edge": "#94a3b8",
                "annotation_text": "#0f172a",
                "normal": "#0284c7",
                "anomaly": "#f97316",
                "duration": "#16a34a",
            }

        return {
            "figure_bg": "#111827",
            "axes_bg": "#0f172a",
            "text": "#e5e7eb",
            "label": "#cbd5e1",
            "grid": "#1f2937",
            "spine": "#334155",
            "legend_bg": "#111827",
            "legend_edge": "#334155",
            "annotation_bg": "#111827",
            "annotation_edge": "#334155",
            "annotation_text": "#e5e7eb",
            "normal": "#38bdf8",
            "anomaly": "#f97316",
            "duration": "#22c55e",
        }

    def apply_plot_theme(self):
        colors = self.get_theme_colors()

        self.figure.patch.set_facecolor(colors["figure_bg"])
        self.ax.set_facecolor(colors["axes_bg"])

        self.ax.tick_params(axis="x", colors=colors["text"])
        self.ax.tick_params(axis="y", colors=colors["text"])

        self.ax.title.set_color(colors["text"])
        self.ax.xaxis.label.set_color(colors["label"])
        self.ax.yaxis.label.set_color(colors["label"])

        for spine in self.ax.spines.values():
            spine.set_color(colors["spine"])

        self.ax.grid(
            True,
            color=colors["grid"],
            linestyle="--",
            linewidth=0.5,
            alpha=0.45
        )

    def style_legend(self):
        colors = self.get_theme_colors()

        legend = self.ax.legend()

        if legend:
            legend.get_frame().set_facecolor(colors["legend_bg"])
            legend.get_frame().set_edgecolor(colors["legend_edge"])
            legend.get_frame().set_alpha(0.92)

            for text in legend.get_texts():
                text.set_color(colors["text"])

    def _prepare_plot(self, data, user_id, reset_index=False):
        self.ax.clear()
        self._hover_annotation = None
        self.apply_plot_theme()

        user_data = data[data["user_id"] == user_id]

        if reset_index:
            user_data = user_data.reset_index(drop=True)

        return user_data

    def plot_user_activity(self, data, user_id):
        user_data = self._prepare_plot(data, user_id, reset_index=True)
        self.reset_hover_data()

        colors = self.get_theme_colors()

        normal = user_data[user_data["anomaly"] == 1]
        anomalies = user_data[user_data["anomaly"] == -1]

        normal_scatter = self.ax.scatter(
            normal["login_hour"],
            normal["actions_count"],
            label=self.tr("plot_normal"),
            color=colors["normal"],
            s=60,
            picker=True
        )

        anomaly_scatter = self.ax.scatter(
            anomalies["login_hour"],
            anomalies["actions_count"],
            label=self.tr("plot_anomaly"),
            color=colors["anomaly"],
            s=90,
            edgecolors="white" if self.get_current_theme() == "dark" else "#0f172a",
            linewidths=1.2,
            picker=True
        )

        normal_hover = []

        for _, row in normal.iterrows():
            note = self.format_normal_note(row)
            note_text = f"\n{self.tr('plot_note')}: {note}" if note else ""

            normal_hover.append(
                f"{self.tr('plot_user')}: {row['username']}\n"
                f"{self.tr('plot_login_hour')}: {row['login_hour']}\n"
                f"{self.tr('plot_actions_count')}: {row['actions_count']}\n"
                f"{self.tr('plot_session_duration')}: {row['session_duration']}\n"
                f"{self.tr('plot_status')}: {self.tr('plot_normal')}"
                f"{note_text}"
            )

        anomaly_hover = []

        for _, row in anomalies.iterrows():
            anomaly_hover.append(
                f"{self.tr('plot_user')}: {row['username']}\n"
                f"{self.tr('plot_login_hour')}: {row['login_hour']}\n"
                f"{self.tr('plot_actions_count')}: {row['actions_count']}\n"
                f"{self.tr('plot_session_duration')}: {row['session_duration']}\n"
                f"{self.tr('plot_status')}: {self.tr('plot_anomaly')}\n"
                f"{self.tr('plot_reason')}: {self.format_model_reason(row)}"
            )

        self._hover_points = [normal_scatter, anomaly_scatter]
        self._hover_data = [normal_hover, anomaly_hover]

        self.ax.set_title(self.tr("plot_activity_title"))
        self.ax.set_xlabel(self.tr("plot_login_hour"))
        self.ax.set_ylabel(self.tr("plot_actions_count"))
        self.ax.margins(0.1)

        self.apply_plot_theme()
        self.style_legend()
        self.figure.tight_layout()
        self.draw()

    def plot_failed_attempts(self, data, user_id):
        user_data = self._prepare_plot(data, user_id, reset_index=True)
        self.reset_hover_data()

        x = range(len(user_data))
        y = user_data["failed_attempts"]

        self.ax.bar(x, y, color="#f59e0b")
        self.ax.set_title(self.tr("plot_failed_attempts_title"))
        self.ax.set_xlabel(self.tr("plot_session"))
        self.ax.set_ylabel(self.tr("plot_errors_count"))

        self.apply_plot_theme()
        self.figure.tight_layout()
        self.draw()

    def plot_session_duration(self, data, user_id):
        user_data = self._prepare_plot(data, user_id, reset_index=True)
        self.reset_hover_data()

        colors = self.get_theme_colors()

        x = range(len(user_data))
        y = user_data["session_duration"]

        self.ax.plot(x, y, marker="o", color=colors["duration"])
        self.ax.set_title(self.tr("plot_duration_title"))
        self.ax.set_xlabel(self.tr("plot_session"))
        self.ax.set_ylabel(self.tr("plot_duration"))

        self.apply_plot_theme()
        self.figure.tight_layout()
        self.draw()

    def plot_anomaly_distribution(self, data, user_id):
        user_data = self._prepare_plot(data, user_id)
        self.reset_hover_data()

        colors = self.get_theme_colors()

        normal_count = len(user_data[user_data["anomaly"] == 1])
        anomaly_count = len(user_data[user_data["anomaly"] == -1])

        labels = [self.tr("plot_normal"), self.tr("plot_anomaly_plural")]
        values = [normal_count, anomaly_count]
        bar_colors = [colors["normal"], colors["anomaly"]]

        self.ax.bar(labels, values, color=bar_colors)
        self.ax.set_title(self.tr("plot_anomaly_distribution_title"))
        self.ax.set_ylabel(self.tr("plot_records_count"))

        self.apply_plot_theme()
        self.figure.tight_layout()
        self.draw()

    def plot_deviations(self, data, user_id):
        user_data = self._prepare_plot(data, user_id, reset_index=True)
        self.reset_hover_data()

        if user_data.empty:
            self.draw()
            return

        colors = self.get_theme_colors()
        x = range(len(user_data))

        login_line, = self.ax.plot(
            x,
            user_data["login_hour_dev"],
            marker="o",
            label=self.tr("plot_login_deviation")
        )

        actions_line, = self.ax.plot(
            x,
            user_data["actions_dev"],
            marker="o",
            label=self.tr("plot_activity_deviation")
        )

        duration_line, = self.ax.plot(
            x,
            user_data["duration_dev"],
            marker="o",
            label=self.tr("plot_duration_deviation")
        )

        login_scatter = self.ax.scatter(
            x,
            user_data["login_hour_dev"],
            s=70,
            color=login_line.get_color(),
            picker=True
        )

        actions_scatter = self.ax.scatter(
            x,
            user_data["actions_dev"],
            s=70,
            color=actions_line.get_color(),
            picker=True
        )

        duration_scatter = self.ax.scatter(
            x,
            user_data["duration_dev"],
            s=70,
            color=duration_line.get_color(),
            picker=True
        )

        hover_texts = []

        for i, row in user_data.iterrows():
            status = self.tr("plot_anomaly") if row["anomaly"] == -1 else self.tr("plot_normal")

            extra_text = ""

            if row["anomaly"] == -1:
                extra_text = (
                    f"\n{self.tr('plot_reason')}: "
                    f"{self.format_model_reason(row)}"
                )
            else:
                note = self.format_normal_note(row)

                if note:
                    extra_text = (
                        f"\n{self.tr('plot_note')}: "
                        f"{note}"
                    )

            hover_texts.append(
                f"{self.tr('plot_session')}: {i + 1}\n"
                f"{self.tr('plot_login_deviation')}: {row['login_hour_dev']:.2f}\n"
                f"{self.tr('plot_activity_deviation')}: {row['actions_dev']:.2f}\n"
                f"{self.tr('plot_duration_deviation')}: {row['duration_dev']:.2f}\n"
                f"{self.tr('plot_status')}: {status}"
                f"{extra_text}"
            )

        self._hover_points = [login_scatter, actions_scatter, duration_scatter]
        self._hover_data = [hover_texts, hover_texts, hover_texts]

        anomalies = user_data[user_data["anomaly"] == -1]

        if not anomalies.empty:
            self.ax.scatter(
                anomalies.index,
                anomalies["actions_dev"],
                s=130,
                color=colors["anomaly"],
                edgecolors="white" if self.get_current_theme() == "dark" else "#0f172a",
                linewidths=1.5,
                label=self.tr("plot_anomaly"),
                picker=False,
                zorder=5
            )

        self.ax.set_title(self.tr("plot_deviation_profile_title"))
        self.ax.set_xlabel(self.tr("plot_session"))
        self.ax.set_ylabel(self.tr("plot_deviation_value"))
        self.ax.margins(0.1)

        self.apply_plot_theme()
        self.style_legend()
        self.figure.tight_layout()
        self.draw()

    def format_model_reason(self, row):
        reasons = []

        model_reason = str(row.get("model_reason", ""))

        if "activity" in model_reason:
            reasons.append(self.tr("reason_high_activity"))

        if "duration" in model_reason:
            reasons.append(self.tr("reason_unusual_duration"))

        if "login_time" in model_reason:
            reasons.append(self.tr("reason_unusual_login_time"))

        if "failed_attempts" in model_reason:
            reasons.append(self.tr("reason_failed_attempts"))

        if not reasons:
            reasons.append(self.tr("reason_combined_behavior"))

        return ", ".join(reasons)

    def format_normal_note(self, row):
        notes = []

        behavior_reason = str(row.get("behavior_reason", ""))

        if "activity" in behavior_reason:
            notes.append(self.tr("note_high_activity_normal"))

        if "duration" in behavior_reason:
            notes.append(self.tr("note_unusual_duration_normal"))

        if "login_time" in behavior_reason:
            notes.append(self.tr("note_unusual_login_time_normal"))

        return ", ".join(notes)

    def on_hover(self, event):
        if self._hover_annotation is None:
            return

        if event.inaxes != self.ax:
            if self._hover_annotation.get_visible():
                self._hover_annotation.set_visible(False)
                self.draw_idle()
            return

        for scatter, data_list in zip(self._hover_points, self._hover_data):
            contains, info = scatter.contains(event)

            if contains:
                index = info["ind"][0]
                point_data = data_list[index]

                x, y = scatter.get_offsets()[index]
                self._hover_annotation.xy = (x, y)
                self._hover_annotation.set_text(point_data)

                if event.xdata is not None and event.ydata is not None:
                    x_offset = 12
                    y_offset = 12

                    x_min, x_max = self.ax.get_xlim()
                    y_min, y_max = self.ax.get_ylim()

                    if event.xdata > (x_min + x_max) / 2:
                        x_offset = -170

                    if event.ydata > (y_min + y_max) / 2:
                        y_offset = -90

                    self._hover_annotation.set_position((x_offset, y_offset))

                self._hover_annotation.set_visible(True)
                self.draw_idle()
                return

        if self._hover_annotation.get_visible():
            self._hover_annotation.set_visible(False)
            self.draw_idle()

    def create_hover_annotation(self):
        colors = self.get_theme_colors()

        self._hover_annotation = self.ax.annotate(
            "",
            xy=(0, 0),
            xytext=(12, 12),
            textcoords="offset points",
            bbox=dict(
                boxstyle="round,pad=0.4",
                fc=colors["annotation_bg"],
                ec=colors["annotation_edge"],
                alpha=0.96
            ),
            color=colors["annotation_text"]
        )

        self._hover_annotation.set_visible(False)

    def reset_hover_data(self):
        self._hover_points = []
        self._hover_data = []
        self.create_hover_annotation()

    def clear_plot(self):
        self.ax.clear()
        self._hover_annotation = None
        self.apply_plot_theme()
        self.reset_hover_data()
        self.ax.set_title(self.tr("plot_select_user_title"))
        self.figure.tight_layout()
        self.draw()