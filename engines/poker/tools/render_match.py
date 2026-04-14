"""Run a rendered heads-up match between two selectable agent strategies."""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from agents.agent_random import Player as RandomPlayer
from agents.agent_strong_hand import Player as StrongHandPlayer
from agents.agent_pro import Player as ProPlayer
from gym_env.env import HoldemTable

AGENT_TYPES = {
    "Random": RandomPlayer,
    "StrongHand": StrongHandPlayer,
    "Pro": ProPlayer,
}


def parse_args():
    parser = argparse.ArgumentParser(description="Render a heads-up neuron poker match.")
    parser.add_argument("--player1", default="StrongHand", choices=sorted(AGENT_TYPES))
    parser.add_argument("--player2", default="Random", choices=sorted(AGENT_TYPES))
    parser.add_argument("--stack", type=int, default=500)
    parser.add_argument("--max-hands", type=int, default=None)
    parser.add_argument("--stats-dir", default="log/render_stats")
    return parser.parse_args()


def build_agent(name: str):
    return AGENT_TYPES[name](name=name)


def to_jsonable(value: Any):
    """Recursively convert numpy/scalar-like values to plain JSON-serializable objects."""
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(v) for v in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:  # pylint: disable=broad-except
            pass
    return value


def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

    env = HoldemTable(
        initial_stacks=args.stack,
        render=True,
        funds_plot=False,
        max_hands=args.max_hands,
    )
    env.add_player(build_agent(args.player1))
    env.add_player(build_agent(args.player2))
    env.reset()

    stats_dir = Path(args.stats_dir)
    stats_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    funds_path = stats_dir / f"funds_{args.player1}_vs_{args.player2}_{ts}.csv"
    env.funds_history.to_csv(funds_path, index=False)

    summary_path = stats_dir / f"summary_{args.player1}_vs_{args.player2}_{ts}.json"
    summary = {
        "player1": args.player1,
        "player2": args.player2,
        "initial_stack": args.stack,
        "max_hands": args.max_hands,
        "winner_ix": env.winner_ix,
        "final_stacks": [player.stack for player in env.players],
        "funds_rows": len(env.funds_history),
    }
    summary_path.write_text(json.dumps(to_jsonable(summary), indent=2), encoding="utf-8")

    hands_path = stats_dir / f"hands_{args.player1}_vs_{args.player2}_{ts}.json"
    hands_path.write_text(json.dumps(to_jsonable(env.hand_results), indent=2), encoding="utf-8")

    print(f"STATS: funds_csv={funds_path}")
    print(f"STATS: summary_json={summary_path}")
    print(f"STATS: hands_json={hands_path}")


if __name__ == "__main__":
    main()
