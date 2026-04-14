"""Smoke tests that prove the poker engine is simulating real hands."""

from agents.agent_random import Player as RandomPlayer
from agents.agent_strong_hand import Player as StrongHandPlayer
from agents.agent_pro import Player as ProPlayer
from gym_env.env import HoldemTable
from gym_env.enums import Action


def _setup_env(*players, max_hands=None):
    env = HoldemTable(initial_stacks=100, render=False, funds_plot=False, max_hands=max_hands)
    for player in players:
        env.add_player(player)
    return env


def test_random_simulation_progresses():
    env = _setup_env(RandomPlayer(), RandomPlayer(), max_hands=1)
    env.reset()
    assert env.done
    assert len(env.funds_history) >= 1
    stacks = [player.stack for player in env.players]
    assert abs(stacks[0] - stacks[1]) > 1e-6
    assert env.winner_ix is not None


def test_strong_hand_agent_decisions():
    agent = StrongHandPlayer()
    strong_actions = {Action.RAISE_POT, Action.CALL}
    strong_info = {"player_cards": ["AS", "KH"]}
    assert agent.action(strong_actions, None, strong_info) == Action.RAISE_POT

    weak_actions = {Action.FOLD, Action.CHECK, Action.CALL}
    weak_info = {"player_cards": ["2C", "6D"]}
    assert agent.action(weak_actions, None, weak_info) == Action.FOLD


def test_strong_hand_vs_random():
    env = _setup_env(StrongHandPlayer(), RandomPlayer(), max_hands=1)
    for _ in range(2):
        env.reset()
        assert env.done
        assert env.winner_ix is not None

def test_pro_agent_decisions():
    agent = ProPlayer()
    actions = {Action.RAISE_POT, Action.CALL, Action.FOLD, Action.CHECK}
    
    # High equity
    high_equity_info = {
        "player_data": {"equity_to_river_alive": 0.9},
        "community_data": {"stage": [True, False, False, False], "community_pot": 20, "current_round_pot": 5}
    }
    assert agent.action(actions, None, high_equity_info) in [Action.RAISE_POT, Action.ALL_IN, Action.RAISE_2POT]

    # Low equity
    low_equity_info = {
        "player_data": {"equity_to_river_alive": 0.1},
        "community_data": {"stage": [True, False, False, False], "community_pot": 20, "current_round_pot": 5}
    }
    assert agent.action(actions, None, low_equity_info) in [Action.FOLD, Action.CHECK]

def test_pro_vs_random():
    env = _setup_env(ProPlayer(), RandomPlayer(), max_hands=1)
    for _ in range(2):
        env.reset()
        assert env.done
        assert env.winner_ix is not None
