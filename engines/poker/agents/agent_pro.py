"""Pro player strategy with advanced heuristics."""

from gym_env.enums import Action

class Player:
    """Advanced heuristic player evaluating equity and pot odds."""

    def __init__(self, name="Pro"):
        """Initialization of an agent"""
        self.equity_alive = 0
        self.actions = []
        self.last_action_in_stage = ''
        self.temp_stack = []
        self.name = name
        self.autoplay = True

    def action(self, action_space, observation, info):
        """Mandatory method that calculates the move based on the observation array and the action space."""
        _ = observation

        # Fallback to 0 if not present
        equity = info.get('player_data', {}).get('equity_to_river_alive', 0)
        community_data = info.get('community_data', {})
        stage_one_hot = community_data.get('stage', [True, False, False, False])
        
        # Determine the current stage
        is_preflop = stage_one_hot[0]
        is_flop = stage_one_hot[1]
        is_turn = stage_one_hot[2]
        # is_river = stage_one_hot[3]
        
        # Calculate dynamic thresholds
        if is_preflop:
            raise_threshold = 0.60
            call_threshold = 0.40
        elif is_flop:
            raise_threshold = 0.65
            call_threshold = 0.45
        elif is_turn:
            raise_threshold = 0.70
            call_threshold = 0.50
        else: # River
            raise_threshold = 0.75
            call_threshold = 0.55
            
        # Extract pot details (normalized, but still proportional)
        pot_size = community_data.get('community_pot', 0) + community_data.get('current_round_pot', 0)
        
        # If equity is extremely high, we play very aggressively
        if equity >= 0.85:
            if Action.ALL_IN in action_space and pot_size > 10: 
                return Action.ALL_IN
            elif Action.RAISE_2POT in action_space:
                return Action.RAISE_2POT
            elif Action.RAISE_POT in action_space:
                return Action.RAISE_POT
            elif Action.RAISE_HALF_POT in action_space:
                return Action.RAISE_HALF_POT
            elif Action.CALL in action_space:
                return Action.CALL

        # Strong hand
        if equity >= raise_threshold:
            if Action.RAISE_POT in action_space and equity > raise_threshold + 0.1:
                return Action.RAISE_POT
            elif Action.RAISE_HALF_POT in action_space:
                return Action.RAISE_HALF_POT
            elif Action.CALL in action_space:
                return Action.CALL

        # Marginal hand (Call or check)
        if equity >= call_threshold:
            if Action.CALL in action_space:
                return Action.CALL

        # Default actions: Check if possible, otherwise Fold
        if Action.CHECK in action_space:
            return Action.CHECK
            
        return Action.FOLD
