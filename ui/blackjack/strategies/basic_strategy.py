from .base import StrategyBase, Action
from ..models.table_state import TableState, Hand

class BasicStrategy(StrategyBase):
    """Standard Basic Strategy (Wizard of Odds style)."""
    
    def suggest(self, state: TableState) -> Action:
        hand = state.current_hand
        dealer_val = state.dealer_hand.total # The upcard value
        
        # Check for split first
        if len(hand.cards) == 2 and hand.cards[0].rank == hand.cards[1].rank:
            action = self._should_split(hand.cards[0].rank.value, dealer_val)
            if action: return action
            
        # Check for soft hand
        if hand.is_soft:
            return self._soft_total(hand.total, dealer_val)
        
        # Default to hard total
        return self._hard_total(hand.total, dealer_val)

    def _should_split(self, rank_char: str, dealer_val: int) -> Action:
        # A,A and 8,8: Always split
        if rank_char in ['A', '8']: return Action.SPLIT
        # 10s: Never split
        if rank_char in ['T', 'J', 'Q', 'K']: return None
        # 9,9: Split except vs 7, 10, A
        if rank_char == '9':
            if dealer_val in [7, 10, 11]: return None
            return Action.SPLIT
        # 7,7: Split vs 2-7
        if rank_char == '7':
            if 2 <= dealer_val <= 7: return Action.SPLIT
        # 6,6: Split vs 2-6
        if rank_char == '6':
            if 2 <= dealer_val <= 6: return Action.SPLIT
        # 4,4: Split vs 5-6 (only if DAS allowed, but let's be conservative)
        if rank_char == '4':
            if dealer_val in [5, 6]: return Action.SPLIT
        # 2,2 and 3,3: Split vs 2-7
        if rank_char in ['2', '3']:
            if 2 <= dealer_val <= 7: return Action.SPLIT
        return None

    def _soft_total(self, total: int, dealer_val: int) -> Action:
        if total >= 19: return Action.STAND
        if total == 18:
            if dealer_val in [2, 3, 4, 5, 6]: return Action.DOUBLE
            if dealer_val in [9, 10, 11]: return Action.HIT
            return Action.STAND
        # Soft 13-17: Double vs 4,5,6 or Hit
        if 13 <= total <= 17:
            if 4 <= dealer_val <= 6: return Action.DOUBLE
            return Action.HIT
        return Action.HIT

    def _hard_total(self, total: int, dealer_val: int) -> Action:
        if total >= 17: return Action.STAND
        if 13 <= total <= 16:
            if 2 <= dealer_val <= 6: return Action.STAND
            return Action.HIT
        if total == 12:
            if 4 <= dealer_val <= 6: return Action.STAND
            return Action.HIT
        if total == 11: return Action.DOUBLE
        if total == 10:
            if 2 <= dealer_val <= 9: return Action.DOUBLE
            return Action.HIT
        if total == 9:
            if 3 <= dealer_val <= 6: return Action.DOUBLE
            return Action.HIT
        return Action.HIT
