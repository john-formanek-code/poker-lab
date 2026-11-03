import sys
import os
import gym
import numpy as np
import pandas as pd
import importlib
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QComboBox, QSlider, QSpinBox, QFrame, QGroupBox, QScrollArea)
from PySide6.QtCore import Qt, QTimer, Slot
from .poker_view import PokerView
from engines.poker.gym_env.env import PlayerShell

class SeatConfigWidget(QGroupBox):
    def __init__(self, seat_index):
        super().__init__(f"Seat {seat_index}")
        layout = QVBoxLayout(self)
        
        self.agent_combo = QComboBox()
        self.agent_combo.addItems([
            "Random Player",
            "Pro Player",
            "Equity Player",
            "Strong Hand Player",
            "Keypress (Human)"
        ])
        layout.addWidget(self.agent_combo)
        
        self.name_label = QLabel(f"Player {seat_index}")
        layout.addWidget(self.name_label)

    def get_agent(self):
        choice = self.agent_combo.currentText()
        if choice == "Random Player":
            from agents.agent_random import Player
            return Player(name=f"Rand_{self.title()[-1]}")
        elif choice == "Pro Player":
            from agents.agent_pro import Player
            return Player(name=f"Pro_{self.title()[-1]}")
        elif choice == "Equity Player":
            from agents.agent_consider_equity import Player
            return Player(name=f"Eq_{self.title()[-1]}", min_call_equity=.5, min_bet_equity=-.5)
        elif choice == "Strong Hand Player":
            from agents.agent_strong_hand import Player
            return Player(name=f"Strong_{self.title()[-1]}")
        elif choice == "Keypress (Human)":
            from agents.agent_keypress import Player
            return Player(name=f"Human_{self.title()[-1]}")
        return None

class PokerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.env = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._game_step)
        
        main_layout = QHBoxLayout(self)

        # Left side: Table View & Controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        main_layout.addWidget(left_widget, 2)

        self.table_view = PokerView()
        left_layout.addWidget(self.table_view)

        # Status & Controls
        self.status_label = QLabel("Configure seats and press Start")
        self.status_label.setObjectName("status_bar")
        left_layout.addWidget(self.status_label)

        controls_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Simulation")
        self.start_btn.clicked.connect(self._toggle_simulation)
        self.start_btn.setMinimumHeight(40)
        self.start_btn.setObjectName("action_btn")
        controls_layout.addWidget(self.start_btn)
        
        controls_layout.addStretch()
        controls_layout.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(10, 1000)
        self.speed_slider.setValue(200)
        controls_layout.addWidget(self.speed_slider)
        
        left_layout.addLayout(controls_layout)

        # Right side: Configuration & Stats
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        main_layout.addWidget(right_widget, 1)

        # Seat Configuration
        config_group = QGroupBox("Table Configuration")
        config_layout = QVBoxLayout(config_group)
        
        num_seats_layout = QHBoxLayout()
        num_seats_layout.addWidget(QLabel("Number of Players:"))
        self.num_seats_spin = QSpinBox()
        self.num_seats_spin.setRange(2, 6)
        self.num_seats_spin.setValue(3)
        self.num_seats_spin.valueChanged.connect(self._update_seat_widgets)
        num_seats_layout.addWidget(self.num_seats_spin)
        config_layout.addLayout(num_seats_layout)
        
        self.seats_scroll = QScrollArea()
        self.seats_scroll.setWidgetResizable(True)
        self.seats_container = QWidget()
        self.seats_vbox = QVBoxLayout(self.seats_container)
        self.seats_scroll.setWidget(self.seats_container)
        config_layout.addWidget(self.seats_scroll)
        
        right_layout.addWidget(config_group)

        # Stats
        stats_group = QGroupBox("Results")
        stats_layout = QVBoxLayout(stats_group)
        self.stats_label = QLabel("No games played yet.")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        right_layout.addWidget(stats_group)
        
        self.seat_widgets = []
        self._update_seat_widgets(self.num_seats_spin.value())
        
        self.winners = []

    def _update_seat_widgets(self, count):
        # Clear existing
        for sw in self.seat_widgets:
            self.seats_vbox.removeWidget(sw)
            sw.deleteLater()
        self.seat_widgets = []
        
        # Add new
        for i in range(count):
            sw = SeatConfigWidget(i)
            self.seat_widgets.append(sw)
            self.seats_vbox.addWidget(sw)

    def _init_env(self):
        env_name = 'neuron_poker-v0'
        # Reset winners when re-initializing
        self.winners = []
        self._update_stats()
        
        self.env = gym.make(env_name, initial_stacks=500, render=False)
        
        for sw in self.seat_widgets:
            agent = sw.get_agent()
            if agent:
                self.env.add_player(agent)

        self.env.reset()
        self.table_view.update_state(self.env.unwrapped)

    def _toggle_simulation(self):
        if self.timer.isActive():
            self.timer.stop()
            self.start_btn.setText("Resume Simulation")
            self.num_seats_spin.setEnabled(True)
            for sw in self.seat_widgets: sw.setEnabled(True)
        else:
            if not self.env or self.start_btn.text() == "Start Simulation":
                self._init_env()
            
            self.num_seats_spin.setEnabled(False)
            for sw in self.seat_widgets: sw.setEnabled(False)
            
            self.timer.start(self.speed_slider.value())
            self.start_btn.setText("Pause Simulation")

    def _game_step(self):
        if not self.env:
            return
            
        raw_env = self.env.unwrapped
        if raw_env.done:
            self.winners.append(raw_env.winner_ix)
            self._update_stats()
            self.env.reset()
        else:
            try:
                raw_env._get_environment()
                action = raw_env.current_player.agent_obj.action(
                    raw_env.legal_moves, raw_env.observation, raw_env.info)
                
                from engines.poker.gym_env.enums import Action
                if Action(action) not in raw_env.legal_moves:
                    raw_env._illegal_move(action)
                else:
                    raw_env._execute_step(Action(action))
            except Exception as e:
                print(f"Error in game step: {e}")
                self.timer.stop()
                self.start_btn.setText("Resume Simulation")
            
        self.table_view.update_state(raw_env)
        self.timer.setInterval(self.speed_slider.value())

    def _update_stats(self):
        if self.winners:
            counts = pd.Series(self.winners).value_counts()
            # Map index to player names
            if self.env:
                names = [p.name for p in self.env.unwrapped.players]
                stats_text = "Win Counts:\n"
                for idx, count in counts.items():
                    name = names[idx] if idx < len(names) else f"Seat {idx}"
                    stats_text += f" {name}: {count}\n"
                self.stats_label.setText(stats_text)
        else:
            self.stats_label.setText("No games played yet.")

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()
