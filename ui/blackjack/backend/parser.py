from typing import Tuple, List, Optional
import re
from ..models.table_state import TableState, Hand
from ..models.card import Card

class MessageParser:
    def parse(self, message: str, state: TableState, seat_index: int = 0):
        tokens = message.split()
        if not tokens:
            return

        command = tokens[0]

        if command == "shuffling":
            state.is_shuffling = True
            # Shuffling affects the whole table

        elif command == "new_hand":
            state.reset_seat(seat_index)
            state.hand_number = int(tokens[1])
            state.bankroll[seat_index] = float(tokens[2])

        elif command == "bet?":
            state.waiting_for[seat_index] = "bet"
            state.message[seat_index] = f"Seat {seat_index}: Place bet"

        elif command == "card_player":
            card_rs = tokens[1]
            hand_id = int(tokens[2]) if len(tokens) > 2 else 0
            card = Card.from_str(card_rs)
            if seat_index not in state.player_seats:
                state.player_seats[seat_index] = {}
            if hand_id not in state.player_seats[seat_index]:
                state.player_seats[seat_index][hand_id] = Hand(id=hand_id)
            state.player_seats[seat_index][hand_id].cards.append(card)

        elif command == "card_dealer_up":
            card = Card.from_str(tokens[1])
            # Dealer upcard is the same for all seats, only update once
            if seat_index == 0:
                state.dealer_hand.cards = [card]

        elif command == "card_dealer":
            card = Card.from_str(tokens[1])
            if seat_index == 0:
                state.dealer_hand.cards.append(card)

        elif command == "card_dealer_hole":
            card = Card.from_str(tokens[1])
            if seat_index == 0:
                state.dealer_hand.cards.append(card)

        elif command == "play?":
            state.waiting_for[seat_index] = "action"
            p_val = int(tokens[1])
            d_val = int(tokens[2])
            hand_id = state.current_hand_id[seat_index]
            hand = state.player_seats[seat_index][hand_id]
            hand.total = abs(p_val)
            hand.is_soft = p_val < 0
            state.dealer_hand.total = d_val
            state.message[seat_index] = f"Seat {seat_index} turn"

        elif command == "player_wins":
            hand_id = state.current_hand_id[seat_index]
            state.player_seats[seat_index][hand_id].result = "win"
            state.waiting_for[seat_index] = None

        elif command == "player_losses":
            hand_id = state.current_hand_id[seat_index]
            state.player_seats[seat_index][hand_id].result = "lose"
            state.waiting_for[seat_index] = None

        elif command == "player_pushes":
            hand_id = state.current_hand_id[seat_index]
            state.player_seats[seat_index][hand_id].result = "push"
            state.waiting_for[seat_index] = None

        elif command == "blackjack_player":
            state.current_hand.result = "blackjack"
            state.message = "Blackjack!"

        elif command == "dealer_busts":
            state.message = f"Dealer busts! You win. ({tokens[1]} vs {tokens[2]})"
            # The player_wins message usually follows or we can set result here
            state.current_hand.result = "win"

        elif command == "player_next_hand":
            state.current_hand_id += 1
            state.message = f"Moving to hand #{state.current_hand_id}"

        elif command == "player_split_ok":
            new_id = int(tokens[1]) if len(tokens) > 1 else 1
            state.player_hands[new_id] = Hand(id=new_id)
            # When splitting, one card goes to each hand.
            # The backend sends card_player messages to update them.
            state.message = "Split successful"

        elif command == "bankroll":
            state.bankroll = float(tokens[1])

        elif command == "bye":
            state.message = "Game over"

        # Track history
        state.history.append(message)
        if len(state.history) > 100:
            state.history.pop(0)
