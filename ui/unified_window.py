import os
import sys
import platform
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QListWidget, QStackedWidget, QLabel, QFrame, QSplitter, QPushButton, QGridLayout)
from PySide6.QtCore import Qt
from common.styles import DARK_THEME

# Import game widgets
from ui.blackjack.ui.blackjack_widget import BlackjackWidget
from ui.blackjack.controllers.game_controller import GameController
from ui.poker.poker_ui import PokerWidget

class InfoPanel(QFrame):
    def __init__(self, title, data_dict):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #050505;
                border: 1px solid #1a1a1a;
                padding: 15px;
            }
            QLabel#title {
                color: #555555;
                font-size: 10px;
                font-weight: bold;
                text-transform: uppercase;
                border: none;
            }
            QLabel#key {
                color: #888888;
                font-size: 11px;
                border: none;
            }
            QLabel#value {
                color: #ffffff;
                font-size: 11px;
                font-weight: bold;
                border: none;
            }
        """)
        layout = QVBoxLayout(self)
        
        t_label = QLabel(title)
        t_label.setObjectName("title")
        layout.addWidget(t_label)
        
        for key, value in data_dict.items():
            row = QHBoxLayout()
            k_label = QLabel(f"{key}:")
            k_label.setObjectName("key")
            v_label = QLabel(str(value))
            v_label.setObjectName("value")
            row.addWidget(k_label)
            row.addStretch()
            row.addWidget(v_label)
            layout.addLayout(row)

class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Header
        header = QVBoxLayout()
        title = QLabel("GAMING SUITE / RESEARCH ARCH")
        title.setStyleSheet("font-size: 32px; font-weight: 900; letter-spacing: 5px; color: #ffffff;")
        header.addWidget(title)
        
        sub = QLabel("UNIFIED ENGINE ORCHESTRATOR V0.1.0_ALPHA")
        sub.setStyleSheet("font-size: 12px; color: #444444; letter-spacing: 2px;")
        header.addWidget(sub)
        main_layout.addLayout(header)

        # Main Grid
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # Panel 1: System Telemetry
        sys_info = {
            "OS": platform.system().upper(),
            "KERNEL": platform.release(),
            "PYTHON": sys.version.split()[0],
            "ARCH": platform.machine(),
            "VENV": "ACTIVE" if hasattr(sys, 'real_prefix') or (sys.base_prefix != sys.prefix) else "GLOBAL"
        }
        grid.addWidget(InfoPanel("SYSTEM TELEMETRY", sys_info), 0, 0)
        
        # Panel 2: Engine Diagnostics
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bj_path = os.path.join(PROJECT_ROOT, "engines", "blackjack", "blackjack")
        
        eng_info = {
            "BJ_CORE": "READY" if os.path.exists(bj_path) else "MISSING",
            "POKER_GYM": "REGISTERED",
            "RENDERER": "QPAINTER_NATIVE",
            "ACCEL": "CPP_MONTECARLO",
            "UI_STACK": "PYSIDE6_STEALTH"
        }
        grid.addWidget(InfoPanel("ENGINE DIAGNOSTICS", eng_info), 0, 1)
        
        main_layout.addLayout(grid)

        # Engine Quick Select
        main_layout.addWidget(QLabel("ACTIVE MODULES"))
        
        modules_layout = QHBoxLayout()
        for game in [("BLACKJACK", "C++ STRATEGY ENGINE"), ("POKER", "RL GYM ENVIRONMENT")]:
            m_frame = QFrame()
            m_frame.setStyleSheet("""
                QFrame {
                    background-color: #080808;
                    border: 1px solid #222222;
                    min-height: 120px;
                }
                QFrame:hover {
                    border-color: #ffffff;
                }
            """)
            m_layout = QVBoxLayout(m_frame)
            m_layout.setAlignment(Qt.AlignCenter)
            
            m_title = QLabel(game[0])
            m_title.setStyleSheet("font-size: 18px; font-weight: bold; border: none; color: #ffffff;")
            m_layout.addWidget(m_title, 0, Qt.AlignCenter)
            
            m_desc = QLabel(game[1])
            m_desc.setStyleSheet("font-size: 10px; border: none; color: #555555;")
            m_layout.addWidget(m_desc, 0, Qt.AlignCenter)
            
            modules_layout.addWidget(m_frame)
        
        main_layout.addLayout(modules_layout)
        main_layout.addStretch()
        
        # Footer Bar
        footer = QHBoxLayout()
        footer.addWidget(QLabel("READY // SESSION_ID: " + os.urandom(4).hex().upper()))
        footer.addStretch()
        footer.addWidget(QLabel("INTERNAL_USE_ONLY"))
        for i in range(footer.count()):
            w = footer.itemAt(i).widget()
            if w: w.setStyleSheet("color: #222222; font-size: 10px;")
        main_layout.addLayout(footer)

class UnifiedWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unified Gaming Suite")
        self.resize(1200, 800)
        self.setStyleSheet(DARK_THEME)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(1)
        main_layout.addWidget(self.splitter)
        
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.addItem("OVERVIEW")
        self.sidebar.addItem("BLACKJACK")
        self.sidebar.addItem("POKER")
        self.sidebar.setMaximumWidth(220)
        self.sidebar.currentRowChanged.connect(self._change_page)
        self.splitter.addWidget(self.sidebar)
        
        self.stack = QStackedWidget()
        self.splitter.addWidget(self.stack)
        
        self.stack.addWidget(DashboardWidget())
        
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bj_binary = os.path.join(PROJECT_ROOT, "engines", "blackjack", "blackjack")
        self.bj_controller = GameController(bj_binary)
        self.bj_widget = BlackjackWidget(self.bj_controller)
        self.stack.addWidget(self.bj_widget)
        
        self.poker_widget = PokerWidget()
        self.stack.addWidget(self.poker_widget)
        
        self.sidebar.setCurrentRow(0)
        self.splitter.setSizes([220, 980])

    def _change_page(self, index):
        self.stack.setCurrentIndex(index)

    def closeEvent(self, event):
        self.bj_controller.stop_game()
        if hasattr(self.poker_widget, 'timer'):
            self.poker_widget.timer.stop()
        event.accept()


# Alias for compatibility
UnifiedGamingWindow = UnifiedWindow
