import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Set up paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Add engines/poker to sys.path for poker imports
sys.path.append(os.path.join(PROJECT_ROOT, "engines", "poker"))
# Add root to sys.path for ui.blackjack and common imports
sys.path.append(PROJECT_ROOT)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Unified Gaming Suite")
    
    # Import UnifiedWindow here after sys.path is set
    from ui.unified_window import UnifiedWindow
    
    window = UnifiedWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
