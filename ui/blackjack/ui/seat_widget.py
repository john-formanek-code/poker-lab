from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt
from .hand_widget import HandWidget
from ..models.table_state import Hand
from typing import Dict

class SeatWidget(QWidget):
    def __init__(self, seat_index: int):
        super().__init__()
        self.seat_index = seat_index
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)

        self.info_label = QLabel(f"Seat {seat_index}")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #f1c40f;")
        self.layout.addWidget(self.info_label)

        self.hands_layout = QHBoxLayout()
        self.layout.addLayout(self.hands_layout)
        
        self.hand_widgets: Dict[int, HandWidget] = {}
        self._add_hand_widget(0)

        self.status_label = QLabel("-")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.status_label)

        self.bankroll_label = QLabel("Bank: 0")
        self.bankroll_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.bankroll_label)

        self.suggestion_label = QLabel("Suggest: -")
        self.suggestion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.suggestion_label.setStyleSheet("color: #2ecc71;")
        self.layout.addWidget(self.suggestion_label)

    def _add_hand_widget(self, hand_id: int):
        hw = HandWidget(f"Hand {hand_id}" if hand_id > 0 else "")
        self.hand_widgets[hand_id] = hw
        self.hands_layout.addWidget(hw)

    def update_seat(self, hands: Dict[int, Hand], bankroll: float, message: str, suggestion: str, current_hand_id: int):
        self.bankroll_label.setText(f"Bank: {bankroll}")
        self.status_label.setText(message)
        self.suggestion_label.setText(f"Suggest: {suggestion.upper() if suggestion else '-'}")

        # Sync hand widgets
        for h_id in hands:
            if h_id not in self.hand_widgets:
                self._add_hand_widget(h_id)
            
            hands[h_id].is_active = (h_id == current_hand_id)
            self.hand_widgets[h_id].update_hand(hands[h_id])
