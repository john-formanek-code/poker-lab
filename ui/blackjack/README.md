# Libre Blackjack GUI

A Python desktop GUI for the `libreblackjack` engine.

## Requirements

- Python 3.11+
- PySide6
- `libreblackjack` backend (must be compiled)

## Setup

1. Build the `libreblackjack` backend:
   ```bash
   ./autogen.sh
   ./configure
   make
   ```
   Ensure the `blackjack` executable is in the root directory.

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   # Or using the pyproject.toml
   pip install .
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Features

- Visual representation of dealer and player cards.
- Real-time updates from the `libreblackjack` engine.
- Supports standard blackjack actions: Bet, Hit, Stand, Double, Split.
- Dark casino-style theme.
- History log of engine messages.

## Architecture

The project follows a modular architecture:
- `models`: Data structures for Cards, Hands, and Table State.
- `backend`: Adapter and Parser for communicating with the `libreblackjack` process.
- `controllers`: Game logic and UI-Backend bridging.
- `ui`: PySide6 components.
