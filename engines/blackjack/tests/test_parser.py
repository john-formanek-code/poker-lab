import unittest
from ui.blackjack.models.table_state import TableState
from ui.blackjack.backend.parser import MessageParser

class TestParser(unittest.TestCase):
    def setUp(self):
        self.state = TableState()
        self.parser = MessageParser()

    def test_new_hand(self):
        self.parser.parse("new_hand 1 1000", self.state)
        self.assertEqual(self.state.hand_number, 1)
        self.assertEqual(self.state.bankroll, 1000)

    def test_card_player(self):
        self.parser.parse("card_player AS", self.state)
        self.assertEqual(len(self.state.player_hands[0].cards), 1)
        self.assertEqual(str(self.state.player_hands[0].cards[0]), "AS")

    def test_play_prompt(self):
        self.parser.parse("play? 16 10", self.state)
        self.assertEqual(self.state.waiting_for, "action")
        self.assertEqual(self.state.current_hand.total, 16)
        self.assertFalse(self.state.current_hand.is_soft)

    def test_soft_hand(self):
        self.parser.parse("play? -17 3", self.state)
        self.assertEqual(self.state.current_hand.total, 17)
        self.assertTrue(self.state.current_hand.is_soft)

if __name__ == "__main__":
    unittest.main()
