from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QSpinBox, QLabel
from PySide6.QtCore import Signal

class ControlsWidget(QWidget):
    bet_requested = Signal(int)
    action_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Betting row
        bet_layout = QHBoxLayout()
        self.bet_spin = QSpinBox()
        self.bet_spin.setRange(1, 10000)
        self.bet_spin.setValue(10)
        self.bet_button = QPushButton("Place Bet")
        self.bet_button.clicked.connect(lambda: self.bet_requested.emit(self.bet_spin.value()))
        bet_layout.addWidget(QLabel("Bet:"))
        bet_layout.addWidget(self.bet_spin)
        bet_layout.addWidget(self.bet_button)
        self.layout.addLayout(bet_layout)

        # Action row
        action_layout = QHBoxLayout()
        self.hit_btn = QPushButton("Hit")
        self.stand_btn = QPushButton("Stand")
        self.double_btn = QPushButton("Double")
        self.split_btn = QPushButton("Split")

        self.hit_btn.clicked.connect(lambda: self.action_requested.emit("hit"))
        self.stand_btn.clicked.connect(lambda: self.action_requested.emit("stand"))
        self.double_btn.clicked.connect(lambda: self.action_requested.emit("double"))
        self.split_btn.clicked.connect(lambda: self.action_requested.emit("split"))

        action_layout.addWidget(self.hit_btn)
        action_layout.addWidget(self.stand_btn)
        action_layout.addWidget(self.double_btn)
        action_layout.addWidget(self.split_btn)
        self.layout.addLayout(action_layout)

    def set_enabled_bet(self, enabled: bool):
        self.bet_spin.setEnabled(enabled)
        self.bet_button.setEnabled(enabled)

    def set_enabled_actions(self, enabled: bool):
        self.hit_btn.setEnabled(enabled)
        self.stand_btn.setEnabled(enabled)
        self.double_btn.setEnabled(enabled)
        self.split_btn.setEnabled(enabled)
