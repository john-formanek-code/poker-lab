import os
from typing import List, Optional, Dict
from PySide6.QtCore import QObject, Signal, QTimer
from ..backend.libreblackjack_adapter import LibreBlackjackAdapter
from ..backend.parser import MessageParser
from ..models.table_state import TableState
from ..models.shoe_tracker import ShoeTracker
from ..strategies.composition_dial_strategy import CompositionDialStrategy
from ..strategies.basic_strategy import BasicStrategy
from ..strategies.base import Action

class GameController(QObject):
    state_updated = Signal()

    def __init__(self, executable_path: str = "./blackjack"):
        super().__init__()
        self.executable_path = executable_path
        self.adapters: Dict[int, LibreBlackjackAdapter] = {}
        self.parser = MessageParser()
        self.state = TableState()
        self.shoe_tracker = ShoeTracker(num_decks=1)
        
        # Initialize strategies with shared shoe tracker
        self.strategies = {
            "Composition Dial": CompositionDialStrategy(self.shoe_tracker),
            "Basic Strategy": BasicStrategy()
        }
        self.current_strategy_key = "Composition Dial"

    def add_seat(self, seat_index: int, args: Optional[List[str]] = None):
        if seat_index in self.adapters:
            return
        
        adapter = LibreBlackjackAdapter(self.executable_path)
        adapter.on_message = lambda msg, idx=seat_index: self._handle_message(msg, idx)
        self.adapters[seat_index] = adapter
        
        # Initialize state for this seat
        self.state.player_seats[seat_index] = {0: {}}
        self.state.reset_seat(seat_index)
        
        # Default args if none provided
        if args is None:
            args = ["--flat_bet=false", "--no_insurance=true", "--decks=1"]
            
        adapter.start(args, 
                      cwd=os.path.dirname(os.path.abspath(self.executable_path)))

    def start_game(self, num_seats_or_args=1):
        if isinstance(num_seats_or_args, list):
            # If a list is passed, assume 1 seat with these args
            self.add_seat(0, num_seats_or_args)
        else:
            for i in range(num_seats_or_args):
                self.add_seat(i)

    def stop_game(self):
        for adapter in self.adapters.values():
            adapter.stop()
        self.adapters.clear()

    def _handle_message(self, message: str, seat_index: int):
        # Update shoe tracker for card messages
        tokens = message.split()
        if tokens:
            cmd = tokens[0]
            if cmd in ["card_player", "card_dealer", "card_dealer_up", "card_dealer_hole"]:
                rank_char = tokens[1][0]
                # Only consume if we haven't seen this specific deal already?
                # Actually, in a real simulation with multiple backends, 
                # they each have their own independent shoe.
                # If we want them to SHARE a shoe, the backend must support it.
                # Since the backend is independent, each seat is its own "table".
                # But the user asked for "more players" on the same backend.
                # Since the backend doesn't support it, we are simulating it with multiple backends.
                # For this to be a "lab", we'll treat them as independent seats.
                self.shoe_tracker.consume(rank_char)
            elif cmd == "shuffling":
                self.shoe_tracker.reset()

        self.parser.parse(message, self.state, seat_index)
        self.state_updated.emit()

    def set_strategy(self, name: str):
        if name in self.strategies:
            self.current_strategy_key = name

    def get_suggestion(self, seat_index: int) -> Optional[str]:
        strategy = self.strategies[self.current_strategy_key]
        
        # Create a temporary local state for the strategy to evaluate this specific seat
        class LocalState:
            def __init__(self, table_state, idx):
                self.current_hand = table_state.player_seats[idx][table_state.current_hand_id[idx]]
                self.dealer_hand = table_state.dealer_hand
                self.waiting_for = table_state.waiting_for[idx]
        
        if self.state.waiting_for.get(seat_index) in ["action", "insurance"]:
            local_state = LocalState(self.state, seat_index)
            action = strategy.suggest(local_state)
            return action.value if action else None
        return None

    def bet(self, seat_index: int, amount: int):
        if seat_index in self.adapters:
            self.adapters[seat_index].send_command(str(amount))

    def hit(self, seat_index: int):
        if seat_index in self.adapters:
            self.adapters[seat_index].send_command("hit")

    def stand(self, seat_index: int):
        if seat_index in self.adapters:
            self.adapters[seat_index].send_command("stand")

    def double(self, seat_index: int):
        if seat_index in self.adapters:
            self.adapters[seat_index].send_command("double")

    def split(self, seat_index: int):
        if seat_index in self.adapters:
            self.adapters[seat_index].send_command("split")

    def insurance(self, seat_index: int, yes: bool):
        if seat_index in self.adapters:
            self.adapters[seat_index].send_command("yes" if yes else "no")
