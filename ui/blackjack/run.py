import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Set up paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(PROJECT_ROOT, "engines", "poker"))
sys.path.append(PROJECT_ROOT)

def main():
    app = QApplication(sys.argv)
    from ui.unified_window import UnifiedWindow
    window = UnifiedWindow()
    # Optionally force to Blackjack tab if desired:
    window.sidebar.setCurrentRow(1)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
