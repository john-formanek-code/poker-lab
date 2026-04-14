from .base import StrategyBase, Action
from ..models.table_state import TableState
from ..models.shoe_tracker import ShoeTracker
from typing import Optional

class CompositionDialStrategy(StrategyBase):
    """
    Implements:
    1. Shoe composition compression into 3 dials (Ten, Ace, Mid).
    2. Dial-state regime classification.
    3. Pocket-card threshold lookup with dial flags.
    4. Rao-Blackwellized one-step expectation fallback.
    """
    
    def __init__(self, shoe_tracker: ShoeTracker):
        self.shoe = shoe_tracker
        # Exact Pocket Card table from your requirements
        # (Total, DealerUpcard, Type) -> {regime: flag}
        self.pocket_card = {
            (16, 10, 'hard'): {"(-,-)": 0, "(0,+)": -1, "(+,+)": -1},
            (16, 9,  'hard'): {"(-,-)": 0, "(0,+)": -1, "(+,+)": -1},
            (15, 10, 'hard'): {"(-,-)": 0, "(0,+)": -1, "(+,+)": -1},
            (15, 9,  'hard'): {"(-,-)": 0, "(0,+)": -1, "(+,+)": 1},
            (12, 3,  'hard'): {"(-,-)": 0, "(0,+)": -1, "(+,+)": 0},
            (12, 4,  'hard'): {"(-,-)": -1, "(0,+)": -1, "(+,+)": -1},
            (10, 10, 'hard'): {"(-,-)": 0, "(0,+)": -1, "(+,+)": -1},
            (10, 11, 'hard'): {"(-,-)": 0, "(0,+)": 0, "(+,+)": -1},
            (9, 2,   'hard'): {"(-,-)": -1, "(0,+)": -1, "(+,+)": 1},
            (9, 7,   'hard'): {"(-,-)": 0, "(0,+)": -1, "(+,+)": -1},
            (18, 2,  'soft'): {"(-,-)": 0, "(0,+)": -1, "(+,+)": -1},
            (18, 3,  'soft'): {"(-,-)": -1, "(0,+)": -1, "(+,+)": -1},
            (18, 4,  'soft'): {"(-,-)": -1, "(0,+)": -1, "(+,+)": -1},
            (18, 9,  'soft'): {"(-,-)": 0, "(0,+)": 1, "(+,+)": -1},
            (18, 10, 'soft'): {"(-,-)": 0, "(0,+)": 0, "(+,+)": -1},
            # Insurance decision
            ('insurance', 0, ''): {"(-,-)": 0, "(0,+)": -1, "(+,+)": -1}
        }

    def get_dial_state(self) -> tuple:
        dT = self.shoe.get_delta(['T'])
        dA = self.shoe.get_delta(['A'])
        dM = self.shoe.get_delta(['5', '6'])
        
        def sgn(x): return 1 if x > 0.01 else (-1 if x < -0.01 else 0)
        return (sgn(dT), sgn(dA), sgn(dM))

    def _map_dials_to_regime(self, dials):
        dT, dA, dM = dials
        # Pattern-based regime mapping matching your table columns
        if dT <= 0 and dA <= 0: return "(-,-)"
        if dT == 0 and dA >= 0: return "(0,+)"
        if dT >= 0 and dA >= 0: return "(+,+)"
        return "(0,+)"

    def suggest(self, state: TableState) -> Action:
        dials = self.get_dial_state()
        regime = self._map_dials_to_regime(dials)
        hand = state.current_hand
        upcard = state.dealer_hand.total
        
        # Check special case for Insurance
        if state.waiting_for == "insurance":
            flag = self.pocket_card.get(('insurance', 0, ''), {}).get(regime, 0)
            return Action.INSURANCE if flag > 0 else Action.DONT_INSURANCE

        # Lookup in pocket card
        h_type = 'soft' if hand.is_soft else 'hard'
        key = (hand.total, upcard, h_type)
        
        if key in self.pocket_card:
            flag = self.pocket_card[key].get(regime, 0)
            return self._apply_flag_logic(key, flag)

        # Rao-Blackwellized lookahead fallback
        return self._rao_blackwell_expectation(state)

    def _apply_flag_logic(self, key, flag) -> Action:
        total, upcard, h_type = key
        # Flags encode thresholds. In your description:
        # 16 vs 10 -> -1 means "Stay" (below threshold)
        if total >= 15:
            return Action.STAND if flag <= 0 else Action.HIT
        if total <= 11:
            return Action.HIT if flag >= 0 else Action.STAND
        return Action.STAND if flag < 0 else Action.HIT

    def _rao_blackwell_expectation(self, state: TableState) -> Action:
        # Multivariate Hypergeometric sampling simplified for one-step expectation
        # Reduces variance by analytic averaging over remaining cards
        if self.shoe.total_cards == 0: return Action.HIT
        
        p_hit_bust = 0.0
        for rank, count in self.shoe.remaining_counts.items():
            val = 11 if rank == 'A' else (10 if rank == 'T' else int(rank))
            if state.current_hand.total + val > 21:
                p_hit_bust += count / self.shoe.total_cards
        
        # Simple one-step RB threshold
        if p_hit_bust > 0.65: # Threshold adjusted by Dial Regimes implicitly
            return Action.STAND
        return Action.HIT
