import numpy as np
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont

class PokerView(QWidget):
    """Professional research-style Poker table rendering."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(650, 450)
        self.env = None
        
        # Monochrome Professional Palette
        self.color_bg = QColor(0, 0, 0)
        self.color_table = QColor(10, 10, 10)
        self.color_border = QColor(30, 30, 30)
        self.color_accent = QColor(255, 255, 255)
        self.color_data = QColor(150, 150, 150)
        self.color_alive = QColor(0, 255, 0, 180) # Matrix Green for data
        self.color_dead = QColor(255, 0, 0, 100)

    def update_state(self, env):
        self.env = env
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.env:
            painter.setPen(self.color_data)
            painter.drawText(self.rect(), Qt.AlignCenter, "INITIALIZING ENGINE...")
            return

        width, height = self.width(), self.height()
        center_x, center_y = width / 2, height / 2
        table_radius = min(width, height) * 0.38
        face_radius = 12

        # Draw Base Table (Minimalist)
        painter.setPen(QPen(self.color_border, 1))
        painter.setBrush(QBrush(self.color_table))
        painter.drawEllipse(center_x - table_radius, center_y - table_radius, 
                           table_radius * 2, table_radius * 2)

        # Community Data
        painter.setPen(self.color_accent)
        painter.setFont(QFont('JetBrains Mono', 10, QFont.Bold))
        
        painter.drawText(center_x - 100, center_y - 20, f"POT: ${self.env.community_pot:,.2f}")
        painter.setPen(self.color_data)
        painter.drawText(center_x - 100, center_y, f"ROUND: ${self.env.current_round_pot:,.2f}")
        painter.setPen(self.color_accent)
        painter.drawText(center_x - 100, center_y + 30, f"CARDS: {self.env.table_cards}")

        # Players
        num_players = len(self.env.players)
        for i in range(num_players):
            degrees = i * (360 / num_players)
            radian = (degrees * (np.pi / 180))
            
            x = (table_radius + 30) * np.cos(radian) + center_x
            y = (table_radius + 30) * np.sin(radian) + center_y
            
            # Status Indicator
            is_active = self.env.player_cycle.alive[i]
            painter.setBrush(QBrush(self.color_alive if is_active else self.color_dead))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x - 5, y - 5, 10, 10)
            
            # Current Player Box
            if hasattr(self.env, 'current_player') and self.env.current_player and i == self.env.current_player.seat:
                painter.setPen(QPen(self.color_accent, 1))
                painter.drawRect(x - 65, y - 45, 130, 65)
            
            # Info
            painter.setPen(self.color_accent)
            p = self.env.players[i]
            equity = int(round(float(p.equity_alive) * 100))
            
            painter.setFont(QFont('JetBrains Mono', 9, QFont.Bold))
            painter.drawText(x + 15 if np.cos(radian) >= 0 else x - 110, y - 10, p.name)
            
            painter.setFont(QFont('JetBrains Mono', 8))
            painter.setPen(self.color_data)
            painter.drawText(x + 15 if np.cos(radian) >= 0 else x - 110, y + 5, f"STK: ${p.stack}")
            painter.drawText(x + 15 if np.cos(radian) >= 0 else x - 110, y + 20, f"EQY: {equity}%")
            
            # Cards
            if p.cards:
                painter.setPen(self.color_accent)
                painter.drawText(x + 15 if np.cos(radian) >= 0 else x - 110, y + 35, f"[{' '.join(map(str, p.cards))}]")

    def reset(self):
        self.update()

    def update_view(self):
        self.update()
