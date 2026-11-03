# Unified Card Games Stack

A unified platform integrating Blackjack and Poker engines with a modern PySide6 UI.

This project combines:
- **Libre Blackjack** (C++ backend by Jeremy Theler) - High-speed Blackjack engine
- **Neuron Poker** (OpenAI Gym by Dick Reuter) - Texas Hold'em poker environment
- Custom PySide6 UI for unified gameplay experience

## Architecture

- **`engines/`**: High-performance game engines.
  - `blackjack/`: C++ backend with strategy support (Libre Blackjack).
  - `poker/`: Gym-based Poker environment (Hold'em) (Neuron Poker).
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
The Blackjack engine is a high-speed C++ implementation supporting multiple decks, various house rules, and advanced strategy evaluation. Based on Libre Blackjack.

### Poker Engine
The Poker engine is an OpenAI Gym compatible environment for training and testing Poker agents, featuring high-speed Monte Carlo simulations (Python/C++). Based on Neuron Poker.

## License

This project is licensed under **GNU General Public License v3** (GPLv3). See [LICENSE](LICENSE) for details.

For attribution information, see [CONTRIBUTORS.md](CONTRIBUTORS.md).

## Attribution

- **Blackjack**: Built on [Libre Blackjack](https://github.com/seamplex/blackjack) by Jeremy Theler
- **Poker**: Built on [Neuron Poker](https://github.com/dickreuter/neuron_poker) by Dick Reuter
- **UI Integration**: Jan Formánek
