from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtCore import Qt, QRectF
from PySide6.QtCore import QPropertyAnimation, Property


class RiskGauge(QWidget):
    def __init__(self):
        super().__init__()
        self._value = 0

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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        size = min(rect.width(), rect.height()) - 20
        x = (rect.width() - size) / 2
        y = (rect.height() - size) / 2

        arc_rect = QRectF(x, y, size, size)

        # фон
        pen = QPen(QColor("#1f2937"), 12)
        painter.setPen(pen)
        painter.drawArc(arc_rect, 180 * 16, 180 * 16)

        # колір по рівню
        if self._value < 30:
            color = "#22c55e"
            label = "Low"
        elif self._value < 60:
            color = "#f59e0b"
            label = "Medium"
        else:
            color = "#ef4444"
            label = "High"

        # Заповнення
        pen = QPen(QColor(color), 12)
        painter.setPen(pen)

        span_angle = int((self._value / 100) * 180 * 16)
        painter.drawArc(arc_rect, 180 * 16, -span_angle)

        # число
        painter.setPen(QColor("white"))
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        painter.setFont(font)

        painter.drawText(rect, Qt.AlignCenter, f"{self._value}")

        # label
        font.setPointSize(10)
        font.setBold(False)
        painter.setFont(font)

        painter.drawText(rect.adjusted(0, 30, 0, 0), Qt.AlignHCenter, label)