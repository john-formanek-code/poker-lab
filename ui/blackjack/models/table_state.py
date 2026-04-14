from dataclasses import dataclass, field
from typing import List, Dict, Optional
from .card import Card

@dataclass
class Hand:
    id: int = 0
    cards: List[Card] = field(default_factory=list)
    bet: int = 0
    total: int = 0
    is_soft: bool = False
    is_active: bool = True
    result: Optional[str] = None # 'win', 'lose', 'push', 'blackjack', 'bust'

@dataclass
class TableState:
    dealer_hand: Hand = field(default_factory=lambda: Hand(id=-1))
    # player_hands[seat_index][hand_id]
    player_seats: Dict[int, Dict[int, Hand]] = field(default_factory=lambda: {0: {0: Hand(id=0)}})
    current_hand_id: Dict[int, int] = field(default_factory=lambda: {0: 0})
    bankroll: Dict[int, float] = field(default_factory=lambda: {0: 0.0})
    waiting_for: Dict[int, Optional[str]] = field(default_factory=lambda: {0: None})
    message: Dict[int, str] = field(default_factory=lambda: {0: ""})
    hand_number: int = 0
    is_shuffling: bool = False
    history: List[str] = field(default_factory=list)

    def reset_round(self):
        self.dealer_hand = Hand(id=-1)
        for seat in self.player_seats:
            self.player_seats[seat] = {0: Hand(id=0)}
            self.current_hand_id[seat] = 0
            self.waiting_for[seat] = None
            self.message[seat] = ""

    def reset_seat(self, seat_index: int):
        self.player_seats[seat_index] = {0: Hand(id=0)}
        self.current_hand_id[seat_index] = 0
        self.waiting_for[seat_index] = None
        self.message[seat_index] = ""
