from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from ..models.table_state import Hand

class CardWidget(QLabel):
    def __init__(self, card_str: str, face_up: bool = True):
        super().__init__()
        self.setObjectName("card")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if not face_up:
            self.setText("??")
            self.setStyleSheet("background-color: #34495e; color: #ecf0f1; border: 2px solid #2c3e50;")
        else:
            self.setText(card_str)
            # Add color for suits
            color = "red" if card_str[1] in ["H", "D"] else "black"
            self.setStyleSheet(f"background-color: white; color: {color}; border: 1px solid #ccc;")

class HandWidget(QWidget):
    def __init__(self, title: str):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.cards_layout = QHBoxLayout()
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(self.cards_layout)

        self.total_label = QLabel("Total: 0")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.total_label)

    def update_hand(self, hand: Hand):
        # Clear cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for card in hand.cards:
            self.cards_layout.addWidget(CardWidget(str(card), card.face_up))

        total_text = f"Total: {hand.total}"
        if hand.is_soft:
            total_text += " (soft)"
        if hand.result:
            total_text += f" - {hand.result.upper()}"
        self.total_label.setText(total_text)

        # Highlight if active
        if hand.is_active:
            self.title_label.setStyleSheet("font-weight: bold; color: #f1c40f;")
        else:
            self.title_label.setStyleSheet("font-weight: normal; color: white;")
