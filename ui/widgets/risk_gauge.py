from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtCore import Qt, QRectF
from PySide6.QtCore import QPropertyAnimation, Property


class RiskGauge(QWidget):
    def __init__(self):
        super().__init__()
        self._value = 0
        self.current_theme = "dark"
        self.animation = None

        self.setMinimumSize(260, 220)

    def get_value(self):
        return self._value

    def set_value_internal(self, value):
        self._value = int(round(value))
        self.update()

    value_prop = Property(float, get_value, set_value_internal)

    def set_value(self, value):
        value = max(0, min(100, value))

        self.animation = QPropertyAnimation(self, b"value_prop")
        self.animation.setDuration(600)
        self.animation.setStartValue(self._value)
        self.animation.setEndValue(value)
        self.animation.start()

    def set_theme(self, theme):
        self.current_theme = theme
        self.update()

    def get_main_window(self):
        parent = self.parent()

        while parent is not None:
            if hasattr(parent, "main_window"):
                return parent.main_window
            parent = parent.parent()

        return None

    def tr_text(self, key, fallback):
        main_window = self.get_main_window()

        if main_window and hasattr(main_window, "tr"):
            return main_window.tr(key)

        return fallback

    def get_theme_colors(self):
        main_window = self.get_main_window()
        theme = getattr(main_window, "current_theme", self.current_theme)

        if theme == "light":
            return {
                "text": "#0f172a",
                "muted": "#475569",
                "track": "#e2e8f0",
                "background": "#ffffff",
            }

        return {
            "text": "#ffffff",
            "muted": "#94a3b8",
            "track": "#1f2937",
            "background": "#111827",
        }

    def get_risk_info(self):
        if self._value < 30:
            return "#22c55e", self.tr_text("risk_low", "Low")

        if self._value < 60:
            return "#f59e0b", self.tr_text("risk_medium", "Medium")

        return "#ef4444", self.tr_text("risk_high", "High")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colors = self.get_theme_colors()
        risk_color, risk_label = self.get_risk_info()

        rect = self.rect()

        size = min(rect.width(), rect.height()) - 34
        size = max(120, size)

        x = (rect.width() - size) / 2
        y = (rect.height() - size) / 2 - 6

        arc_rect = QRectF(x, y, size, size)

        # Фонова дуга
        track_pen = QPen(QColor(colors["track"]), 13)
        track_pen.setCapStyle(Qt.FlatCap)
        painter.setPen(track_pen)
        painter.drawArc(arc_rect, 180 * 16, 180 * 16)

        # Заповнена частина дуги
        value_pen = QPen(QColor(risk_color), 13)
        value_pen.setCapStyle(Qt.FlatCap)
        painter.setPen(value_pen)

        span_angle = int((self._value / 100) * 180 * 16)
        painter.drawArc(arc_rect, 180 * 16, -span_angle)

        # Число
        value_font = QFont()
        value_font.setPointSize(17)
        value_font.setBold(True)
        painter.setFont(value_font)
        painter.setPen(QColor(colors["text"]))

        painter.drawText(
            rect.adjusted(0, -4, 0, 0),
            Qt.AlignCenter,
            str(self._value)
        )

        # Рівень ризику
        label_font = QFont()
        label_font.setPointSize(10)
        label_font.setBold(False)
        painter.setFont(label_font)
        painter.setPen(QColor(colors["text"]))

        painter.drawText(
            rect.adjusted(0, 34, 0, 0),
            Qt.AlignHCenter,
            risk_label
        )