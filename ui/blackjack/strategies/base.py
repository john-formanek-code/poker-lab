from abc import ABC, abstractmethod
from enum import Enum
from ..models.table_state import TableState

class Action(Enum):
    HIT = "hit"
    STAND = "stand"
    DOUBLE = "double"
    SPLIT = "split"
    SURRENDER = "surrender"
    INSURANCE = "yes"
    DONT_INSURANCE = "no"

class StrategyBase(ABC):
    @abstractmethod
    def suggest(self, state: TableState) -> Action:
        """Suggest an action based on the current state."""
        pass
