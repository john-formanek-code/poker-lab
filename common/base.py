from abc import ABC, abstractmethod
from typing import List, Optional

class GameEngine(ABC):
    """Base class for all game engines."""
    
    @abstractmethod
    def start(self, args: Optional[List[str]] = None):
        """Start the engine with provided arguments."""
        pass
        
    @abstractmethod
    def stop(self):
        """Stop the engine and clean up resources."""
        pass
        
    @abstractmethod
    def send_command(self, command: str):
        """Send a command to the engine."""
        pass

class GameUI(ABC):
    """Base class for all game UIs."""
    
    @abstractmethod
    def show(self):
        """Display the UI."""
        pass
        
    @abstractmethod
    def hide(self):
        """Hide the UI."""
        pass
