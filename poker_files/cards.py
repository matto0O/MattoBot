import os
import random
from photo_generator import generateCard
import discord as dc

SPADE_CLR = (0, 0, 0, 100)
HEART_CLR = (199, 54, 44, 100)
DIAMOND_CLR = (34, 189, 132, 100)
CLUB_CLR = (145, 29, 124, 100)

class Card:
    def __init__(self, rank, rank_value, color, find=True):
        self.rank_value = rank_value
        self.rank = rank
        self.color = color
        self.file = self.card_url(find)

    def card_url(self, find) -> dc.File:
        if find:
            try:
                with open(f"cards/{self.rank}{self.color}", 'rb') as file:
                    return dc.File(file)
            except FileNotFoundError:
                pass

        match self.color:
            case 's':
                card_clr = SPADE_CLR
            case 'h':
                card_clr = HEART_CLR
            case 'd':
                card_clr = DIAMOND_CLR
            case 'c':
                card_clr = CLUB_CLR
        with open(generateCard(self.rank, self.color, card_clr), 'rb') as file:
            return dc.File(file)

    def __repr__(self):
        match self.color:
            case 's':
                color_full_name = 'Spades'
            case 'h':
                color_full_name = 'Hearts'
            case 'd':
                color_full_name = 'Diamonds'
            case 'c':
                color_full_name = 'Clubs'

        return f"{self.rank} of {color_full_name}"
    
    def __eq__(self, other):
        return self.rank == other.rank

    def __gt__(self, other):
        return self.rank_value > other.rank_value
    
    def __lt__(self, other):
        return self.rank_value < other.rank_value

class Deck:
    def __init__(self, force_generate=False):
        RANK_VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        self.spade_clr = SPADE_CLR
        self.heart_clr = HEART_CLR
        self.diamond_clr = DIAMOND_CLR
        self.club_clr = CLUB_CLR
        self.cards = []

        folder_path = 'poker_files/cards'
        files = os.listdir(folder_path)

        if not force_generate:
            jpg_files = [file for file in files if file.endswith('.jpg')]

            if len(jpg_files) == 52:
                try:
                    for e, rank in enumerate(RANK_VALUES):
                        self.cards.append(Card(rank, e, 's'))
                        self.cards.append(Card(rank, e, 'h'))
                        self.cards.append(Card(rank, e, 'd'))
                        self.cards.append(Card(rank, e, 'c'))
                    return
                except:
                    self.cards = []

        for filename in files:
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)

        for e, rank in enumerate(RANK_VALUES):
            self.cards.append(Card(rank, e, 's', False))
            self.cards.append(Card(rank, e, 'h', False))
            self.cards.append(Card(rank, e, 'd', False))
            self.cards.append(Card(rank, e, 'c', False))

    def shuffle(self):
        random.shuffle(self.cards)

    def get_card(self) -> Card:
        return self.cards.pop(0)