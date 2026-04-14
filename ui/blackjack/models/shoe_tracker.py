from dataclasses import dataclass, field
from typing import Dict

@dataclass
class ShoeTracker:
    num_decks: int = 1
    initial_counts: Dict[str, int] = field(default_factory=dict)
    remaining_counts: Dict[str, int] = field(default_factory=dict)
    total_cards: int = 0

    def __post_init__(self):
        self.reset()

    def reset(self):
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T']
        for r in ranks:
            # T represents 10, J, Q, K
            multiplier = 4 if r == 'T' else 1
            count = 4 * self.num_decks * multiplier
            self.initial_counts[r] = count
            self.remaining_counts[r] = count
        self.total_cards = 52 * self.num_decks

    def consume(self, rank_char: str):
        if rank_char in ['J', 'Q', 'K']: rank_char = 'T'
        if rank_char in self.remaining_counts and self.remaining_counts[rank_char] > 0:
            self.remaining_counts[rank_char] -= 1
            self.total_cards -= 1

    def get_expected(self, rank_char: str) -> float:
        if rank_char in ['J', 'Q', 'K']: rank_char = 'T'
        initial_total = 52 * self.num_decks
        return (self.initial_counts[rank_char] / initial_total) * self.total_cards

    def get_delta(self, rank_chars: list[str]) -> float:
        if self.total_cards == 0: return 0
        actual = sum(self.remaining_counts.get(r, 0) for r in rank_chars)
        expected = sum(self.get_expected(r) for r in rank_chars)
        return actual - expected
