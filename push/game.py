import numpy as np
import random
import logging


class Card:

    def __init__(self, type_='standard', color=None, number=None, is_banked=False):
        self.type = type_
        self.color = color
        self.number = number
        self.is_banked = is_banked

    def __str__(self):
        return f'{self.type}, {self.color}, {self.number}'


def roll_die():
    colors = ['red', 'purple', 'yellow', 'blue', 'green', 'black']
    color_rolled = random.choice(colors)

    logging.info(f'Die roll: {color_rolled}')

    return color_rolled


class Deck:

    def __init__(self, cards=None):
        if cards is None:
            self.cards = []
            colors = ['red', 'purple', 'yellow', 'blue', 'green']
            for number in range(6):
                for color in colors:
                    for __ in range(3):
                        self.cards.append(Card('standard', color, number))

            for __ in range(12):
                self.cards.append(Card('reverse'))

            for __ in range(18):
                self.cards.append(Card('roll'))

            self.shuffle()

    def shuffle(self):
        logging.info('Deck Shuffled.')
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop(0)

    def is_empty(self):
        return len(self.cards) == 0


class Pile:

    def __init__(self, cards=None):
        if cards is None:
            self.cards = []
        else:
            self.cards = cards

    def valid_addition(self, card_to_add):
        for card in self.cards:
            if card.type == 'reverse':
                return False
            if card.color == card_to_add.color:
                return False
            if card.number == card_to_add.number:
                return False
            if card.type == 'roll' and card_to_add.type == 'roll':
                return False
        return True

    def add_card(self, card_to_add):
        self.cards.append(card_to_add)


class PileGroup:

    def __init__(self, piles=None):
        if piles is None:
            self.piles = [Pile() for __ in range(3)]

    def valid_addition(self, pile_index, card_to_add):
        return self.piles[pile_index].valid_addition(card_to_add)

    def add_card(self, pile_index, card_to_add):
        self.piles[pile_index].add_card(card_to_add)

    def remove_pile(self, pile_index):
        return self.piles.pop(pile_index)

    @property
    def pile_values(self):
        values = []
        for pile in self.piles:
            value = 0
            for card in pile.cards:
                try:
                    value += card.number
                except TypeError:
                    if card.type == 'roll':
                        value -= 6
            values.append(value)
        return values


class Player:

    def __init__(self, name='', card_draw_limit=10, card_min_draw=5):
        self.name = name
        self.card_draw_limit = card_draw_limit
        self.card_min_draw = card_min_draw
        self.cards = []

    def create_piles(self, deck):
        number_of_cards = random.randint(self.card_min_draw, self.card_draw_limit)

        is_reversed = False
        pushed_too_far = False

        piles = PileGroup()

        for __ in range(number_of_cards):
            try:
                card = deck.deal()
            except IndexError:
                break

            if card.type == 'reverse':
                is_reversed = not is_reversed
                continue

            card_added = False
            for pile in piles.piles:
                if pile.valid_addition(card):
                    pile.add_card(card)
                    card_added = True
                    break

            if not card_added:
                pushed_too_far = True

        return is_reversed, pushed_too_far, piles

    def choose_pile(self, pile_group):
        id_pile = min(range(len(pile_group.pile_values)), key=pile_group.pile_values.__getitem__)
        pile = pile_group.remove_pile(id_pile)
        for card in pile.cards:
            if card.type == 'roll':
                self.roll_die()
            else:
                self.cards.append(card)

    def discard_color(self, color):
        for k, card in enumerate(self.cards):
            if card.color == color and not card.is_banked:
                self.cards.pop(k)

    def roll_die(self):
        color = roll_die()
        self.discard_color(color)

    def bank_cards(self, color):
        for card in self.cards:
            if card.color == color:
                card.is_banked = True

    @property
    def sum_cards(self):
        return sum([card.number for card in self.cards if card.type == 'standard'])

    @property
    def num_cards(self):
        return len([card.number for card in self.cards if card.type == 'standard'])


class Game:

    def __init__(self, players):
        self.players = players
        self.is_reversed = False
        self.deck = Deck()

    def play(self):
        player_id = np.arange(self.num_players)
        while not self.deck.is_empty():
            current_player = self.players[player_id[0]]

            logging.info(f'Player {player_id[0]} starts their turn')

            is_reversed, pushed_too_far, piles = current_player.create_piles(self.deck)

            if is_reversed:
                logging.info('Play is reversed')
                player_id = np.roll(player_id, -1)
                player_id = np.flip(player_id)

            if pushed_too_far:
                player_id_to_distribute = player_id[1:4]
                logging.info(f'Player {player_id[0]} pushed too far!')
            else:
                player_id_to_distribute = player_id[:3]

            player_id = np.roll(player_id, -1)

            for idx in player_id_to_distribute:
                self.players[idx].choose_pile(piles)

        return self.end_game()

    @property
    def num_players(self):
        return len(self.players)

    @property
    def score(self):
        return [player.sum_cards for player in self.players]

    def end_game(self):
        max_score = max(self.score)
        count = self.score.count(max_score)

        if count == 1:
            winner = np.argmax(self.score)
            logging.info('Player {} wins!'.format(np.argmax(self.score)))

        else:
            max_id = np.where(np.array(self.score) == max_score)[0]
            num_cards = np.array([player.num_cards for player in self.players])

            winner_num_cards = 0
            winner = None
            for k in max_id:
                if num_cards[k] > winner_num_cards:
                    winner_num_cards = num_cards[k]
                    winner = k

            logging.info('Player {} wins!'.format(winner))

            logging.info(f'Number of cards: {num_cards}')

        logging.info(f'Scores: {self.score}')
        return winner
