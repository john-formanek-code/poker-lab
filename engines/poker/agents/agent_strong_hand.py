"""Simple deterministic agent that raises on strong hands and folds on weak ones."""
from typing import Iterable, Sequence

from gym_env.enums import Action

RANK_ORDER = "23456789TJQKA"
HIGH_THRESHOLD = RANK_ORDER.index("T")


class Player:
    """Deterministic player that evaluates hole cards."""

    def __init__(self, name: str = "StrongHand"):
        self.name = name
        self.autoplay = True
        self.equity_alive = 0
        self.actions = []
        self.last_action_in_stage = ""
        self.temp_stack = []

    def _card_rank_indices(self, cards: Sequence[str]) -> Sequence[int]:
        """Convert hole-card ranks to their indices in RANK_ORDER."""
        result = []
        for card in cards:
            if not card:
                continue
            rank = card[0]
            if rank in RANK_ORDER:
                result.append(RANK_ORDER.index(rank))
        return result

    def _prefers_raise(self, card_indices: Iterable[int]) -> bool:
        """Treat pairs or two high cards as strong."""
        indices = list(card_indices)
        if not indices:
            return False
        if len(indices) == 2 and indices[0] == indices[1]:
            return True
        return all(index >= HIGH_THRESHOLD for index in indices)

    def action(self, action_space, observation, info):
        """Return deterministic decisions for the available legal moves."""
        possible = set(action_space)
        card_indices = self._card_rank_indices(info.get("player_cards", []))
        if self._prefers_raise(card_indices):
            for option in (Action.RAISE_POT, Action.RAISE_HALF_POT, Action.RAISE_2POT, Action.CALL):
                if option in possible:
                    return option
        for option in (Action.FOLD, Action.CHECK):
            if option in possible:
                return option
        return next(iter(possible), Action.FOLD)
