from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel


class StatCard(QFrame):
    def __init__(self, title, value="0"):
        super().__init__()
        self.setObjectName("statCard")

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")

        self.value_label = QLabel(value)
        self.value_label.setObjectName("cardValue")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()

        self.setLayout(layout)

    def set_value(self, value):
        self.value_label.setText(str(value))
        self.value_label.setStyleSheet("")

    def set_value_with_color(self, value, color):
        self.value_label.setText(str(value))
        self.value_label.setStyleSheet(f"color: {color};")
