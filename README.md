# Unified Card Games Stack

This repository unifies multiple card game engines into a single, cohesive stack.

## Architecture

- **`engines/`**: High-performance game engines.
  - `blackjack/`: C++ backend with strategy support.
  - `poker/`: Gym-based Poker environment (Hold'em).
- **`ui/`**: Unified PySide6 User Interface.
  - `unified_window.py`: Main application container with sidebar navigation.
  - `blackjack/`: Specialized widgets for Blackjack table and controls.
  - `poker/`: Specialized `QPainter`-based Poker table visualization.
- **`common/`**: Shared resources like `styles.py` and `base.py`.
- **`main.py`**: Entry point for the unified application suite.

## Getting Started

### Prerequisites

- Python 3.11+
- C++ Compiler (g++ or clang)
- Make (for building the Blackjack engine)

### Setup and Build

To install dependencies and build all engines:

```bash
make all
```

### Run

Launch the unified gaming suite:

```bash
make run
```

## Engines Detail

### Blackjack Engine
The Blackjack engine is a high-speed C++ implementation supporting multiple decks, various house rules, and advanced strategy evaluation.

### Poker Engine
The Poker engine is an OpenAI Gym compatible environment for training and testing Poker agents, featuring high-speed Monte Carlo simulations (Python/C++).

---
*Unified by Gemini CLI*
