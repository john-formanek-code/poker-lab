from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QFrame, QSplitter, QPushButton, QComboBox, QSlider, QSpinBox, QScrollArea
from PySide6.QtCore import Qt, Slot, QTimer
from .hand_widget import HandWidget
from .controls_widget import ControlsWidget
from .seat_widget import SeatWidget
from ..models.table_state import Hand
from ..controllers.game_controller import GameController

class BlackjackWidget(QWidget):
    def __init__(self, controller: GameController):
        super().__init__()
        self.controller = controller
        
        main_layout = QHBoxLayout(self)

        # Left side: Table and Controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        main_layout.addWidget(left_widget, 3)

        # Bankroll and Info header
        header_layout = QHBoxLayout()
        self.hand_label = QLabel("Hand: #0")
        
        header_layout.addWidget(QLabel("Seats:"))
        self.seats_spin = QSpinBox()
        self.seats_spin.setRange(1, 7)
        self.seats_spin.setValue(1)
        self.seats_spin.valueChanged.connect(self._change_seats)
        header_layout.addWidget(self.seats_spin)

        header_layout.addStretch()
        header_layout.addWidget(self.hand_label)
        left_layout.addLayout(header_layout)

        # Table area
        self.table_frame = QFrame()
        self.table_frame.setObjectName("table_container")
        table_layout = QVBoxLayout(self.table_frame)
        
        self.dealer_hand_widget = HandWidget("Dealer")
        table_layout.addWidget(self.dealer_hand_widget)
        
        table_layout.addStretch()

        self.seats_layout = QHBoxLayout()
        table_layout.addLayout(self.seats_layout)
        self.seat_widgets = {}
        
        left_layout.addWidget(self.table_frame)

        # Global Status
        self.status_label = QLabel("Starting simulation...")
        self.status_label.setObjectName("status_bar")
        left_layout.addWidget(self.status_label)

        # Info Layout
        info_layout = QHBoxLayout()
        
        # Global Dial Indicators
        self.dial_label = QLabel("Dials: T:0 A:0 M:0")
        self.dial_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        info_layout.addWidget(self.dial_label)
        
        # Strategy Selection
        info_layout.addStretch()
        info_layout.addWidget(QLabel("Strategy:"))
        self.strat_combo = QComboBox()
        self.strat_combo.addItems(["Composition Dial", "Basic Strategy"])
        self.strat_combo.currentTextChanged.connect(self.controller.set_strategy)
        info_layout.addWidget(self.strat_combo)
        left_layout.addLayout(info_layout)

        # Controls area
        controls_area = QHBoxLayout()
        
        # Simulation Speed
        speed_layout = QVBoxLayout()
        speed_layout.addWidget(QLabel("Sim Delay (ms):"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(10, 1000)
        self.speed_slider.setValue(200)
        speed_layout.addWidget(self.speed_slider)
        controls_area.addLayout(speed_layout)

        self.controls = ControlsWidget()
        self.controls.bet_requested.connect(self.controller.bet)
        self.controls.action_requested.connect(self._handle_action)
        controls_area.addWidget(self.controls)

        # Autoplay toggle
        self.autoplay_btn = QPushButton("Enable Autoplay")
        self.autoplay_btn.setCheckable(True)
        self.autoplay_btn.clicked.connect(self._toggle_autoplay)
        controls_area.addWidget(self.autoplay_btn)
        
        left_layout.addLayout(controls_area)

        # Right side: History
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel("History"))
        self.history_list = QListWidget()
        right_layout.addWidget(self.history_list)
        main_layout.addWidget(right_widget, 1)

        # Initialize seats
        self._change_seats(1)

        # Connect controller
        self.controller.state_updated.connect(self.update_ui)

    def _change_seats(self, count: int):
        # Add new seats
        for i in range(count):
            if i not in self.seat_widgets:
                sw = SeatWidget(i)
                self.seat_widgets[i] = sw
                self.seats_layout.addWidget(sw)
                self.controller.add_seat(i)
        
        # Hide extra seats
        for i in self.seat_widgets:
            self.seat_widgets[i].setVisible(i < count)

    def _handle_action(self, action: str, seat_index: int = 0):
        if action == "hit":
            self.controller.hit(seat_index)
        elif action == "stand":
            self.controller.stand(seat_index)
        elif action == "double":
            self.controller.double(seat_index)
        elif action == "split":
            self.controller.split(seat_index)

    def _toggle_autoplay(self, checked: bool):
        self.autoplay_btn.setText("Disable Autoplay" if checked else "Enable Autoplay")
        if checked:
            QTimer.singleShot(100, self._run_autoplay)

    def _run_autoplay(self):
        if not self.autoplay_btn.isChecked():
            return
        
        state = self.controller.state
        # Process each seat
        for i in range(self.seats_spin.value()):
            waiting = state.waiting_for.get(i)
            if waiting == "bet":
                self.controller.bet(i, 10)
            elif waiting == "action":
                suggestion = self.controller.get_suggestion(i)
                if suggestion:
                    self._handle_action(suggestion, i)
        
        delay = self.speed_slider.value()
        QTimer.singleShot(delay, self._run_autoplay)

    @Slot()
    def update_ui(self):
        state = self.controller.state

        self.hand_label.setText(f"Hand: #{state.hand_number}")
        
        # Update Dials
        dT, dA, dM = self.controller.shoe_tracker.get_delta(['T']), \
                     self.controller.shoe_tracker.get_delta(['A']), \
                     self.controller.shoe_tracker.get_delta(['5', '6'])
        self.dial_label.setText(f"Dials: T:{dT:+.1f} A:{dA:+.1f} M:{dM:+.1f}")

        # Update dealer hand
        self.dealer_hand_widget.update_hand(state.dealer_hand)

        # Update each seat
        for i in range(self.seats_spin.value()):
            if i in self.seat_widgets:
                hands = state.player_seats.get(i, {0: Hand()})
                bankroll = state.bankroll.get(i, 0.0)
                msg = state.message.get(i, "")
                suggestion = self.controller.get_suggestion(i)
                current_hand_id = state.current_hand_id.get(i, 0)
                
                self.seat_widgets[i].update_seat(hands, bankroll, msg, suggestion, current_hand_id)

        # Update history
        current_history_count = self.history_list.count()
        if len(state.history) > current_history_count:
            for i in range(current_history_count, len(state.history)):
                self.history_list.addItem(state.history[i])
            self.history_list.scrollToBottom()
