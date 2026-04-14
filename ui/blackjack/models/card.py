from dataclasses import dataclass
from enum import Enum
from typing import Optional

class Suit(Enum):
    CLUBS = "C"
    DIAMONDS = "D"
    HEARTS = "H"
    SPADES = "S"

    @classmethod
    def from_char(cls, char: str) -> "Suit":
        return {
            "C": cls.CLUBS,
            "D": cls.DIAMONDS,
            "H": cls.HEARTS,
            "S": cls.SPADES
        }[char.upper()]

class Rank(Enum):
    ACE = "A"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "T"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"

    @classmethod
    def from_char(cls, char: str) -> "Rank":
        return {
            "A": cls.ACE,
            "2": cls.TWO,
            "3": cls.THREE,
            "4": cls.FOUR,
            "5": cls.FIVE,
            "6": cls.SIX,
            "7": cls.SEVEN,
            "8": cls.EIGHT,
            "9": cls.NINE,
            "T": cls.TEN,
            "J": cls.JACK,
            "Q": cls.QUEEN,
            "K": cls.KING
        }[char.upper()]

@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit
    face_up: bool = True

    @classmethod
    def from_str(cls, rs: str, face_up: bool = True) -> "Card":
        if len(rs) != 2:
            raise ValueError(f"Invalid card string: {rs}")
        return cls(Rank.from_char(rs[0]), Suit.from_char(rs[1]), face_up)

    def __str__(self) -> str:
        if not self.face_up:
            return "??"
        return f"{self.rank.value}{self.suit.value}"
