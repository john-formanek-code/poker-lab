.PHONY: all blackjack poker clean setup run

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

all: setup blackjack poker

$(VENV)/bin/activate:
	python3 -m venv $(VENV)

setup: $(VENV)/bin/activate
	$(PIP) install -e .

blackjack:
	@if [ ! -f engines/blackjack/blackjack ]; then \
		echo "Building Blackjack Engine..."; \
		cd engines/blackjack && ./configure && $(MAKE); \
	else \
		echo "Blackjack Engine already built."; \
	fi

poker:
	@echo "Poker Engine (Python-based with on-the-fly C++ compilation) is ready."
	@echo "To pre-compile Poker C++ components (optional):"
	@echo "cd engines/poker && ../../$(PYTHON) setup.py build_ext --inplace"

clean:
	cd engines/blackjack && $(MAKE) clean || true
	rm -rf build/ dist/ *.egg-info $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +

run:
	$(PYTHON) main.py
