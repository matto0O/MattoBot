import os
import random
from photo_generator import generateCard
import discord as dc
from .players import Player

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
    
    def __hash__(self) -> int:
        return self.rank_value

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
                        v = e + 2
                        self.cards.append(Card(rank, v, 's'))
                        self.cards.append(Card(rank, v, 'h'))
                        self.cards.append(Card(rank, v, 'd'))
                        self.cards.append(Card(rank, v, 'c'))
                    return
                except:
                    self.cards = []

        for filename in files:
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)

        for e, rank in enumerate(RANK_VALUES):
            v = e + 2
            self.cards.append(Card(rank, v, 's', False))
            self.cards.append(Card(rank, v, 'h', False))
            self.cards.append(Card(rank, v, 'd', False))
            self.cards.append(Card(rank, v, 'c', False))

    def shuffle(self):
        random.shuffle(self.cards)

    def get_card(self) -> Card:
        return self.cards.pop(0)
    
class Hand:
    def __init__(self, table: list, player:Player) -> None:
        self.cards = (player.hand + table)
        self.cards.sort(reverse=True)
        self.player = player
        self.evaluation = None

    def is_sublist(self, list1:list, list2:list):
        return all(elem in list2 for elem in list1) 

    def eval(self) -> int:

        if self.evaluation != None:
            return self.evaluation

        def return_straight(cards:list):
            cards.sort(reverse=True)
            max = []
            curr = [cards[0]]
            for i in range(1, len(cards)):
                if cards[i].rank_value in [cards[i-1].rank_value - 1, cards[i-1].rank_value]:
                    curr.append(cards[i])
                else:
                    if len(curr) > len(max): 
                        max = list(set(curr))
                    curr = [cards[i-1]]
            print("127 - eval,return_straight - max no of straight cards",max)
            if len(max) >=5:
                return True, max
            return False, cards
        
        def return_color(cards:list):
            spades = []
            hearts = []
            diamonds = []
            clubs = []
            for card in cards:
                match card.color:
                    case 's':
                        spades.append(card)
                    case 'h':
                        hearts.append(card)
                    case 'd':
                        diamonds.append(card)
                    case 'c':
                        clubs.append(card)
            if len(spades) >= 5:
                return True, spades
            if len(hearts) >= 5:
                return True, hearts
            if len(diamonds) >= 5:
                return True, diamonds
            if len(clubs) >= 5:
                return True, clubs
            print("155 - eval,return_colors - all colors",spades, hearts, diamonds, clubs)
            return False, cards
        
        def quantities(cards: list):
            quantity = dict()
            for card in cards:
                if card.rank_value in quantity:
                    quantity[card.rank_value].append(card)
                else:
                    quantity[card.rank_value] = [card]
            
            q_sorted = list(quantity.items())
            q_sorted.sort(key=lambda x: len(x[1]), reverse=True)

            best_hand = q_sorted[0][1]
            max_quantity = len(best_hand)
            print("170 - quantities best hand", best_hand, max_quantity)

            match max_quantity:
                case 4:
                    return 7, best_hand + [card for card in cards if card.rank_value != q_sorted[0]][:1]
                case 3:
                    if len(q_sorted[1][1]) >= 2:
                        return 6, best_hand + q_sorted[1][1][:2]
                    return 3, best_hand + [card for card in cards if card.rank_value != q_sorted[0]][:2]
                case 2:
                    if len(q_sorted[1][1]) >= 2:
                        return 2, best_hand + q_sorted[1][1][:2] + [card for card in cards if card.rank_value != q_sorted[0]][:1]
                    return 1, best_hand + [card for card in cards if card.rank_value != q_sorted[0]][:3]
                case 1:
                    return 0, cards[:5]


        # [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

        flush, f_cards = return_color(self.cards)
        straight, s_cards = return_straight(self.cards)

        temp_combination = 0

        print("197 - eval - cards, is flush, is straight",self.cards, flush, straight)

        if flush:
            if self.is_sublist([14,13,12,11,10], list(map(lambda x: x.rank_value, f_cards))):
                self.cards = f_cards
                self.evaluation = 9
                return 9
            color = f_cards[0].color
            sf, sf_cards = return_straight(list(filter(lambda x:x.color == color,s_cards)))
            if sf:
                self.cards = sf_cards
                self.evaluation = 8
                return 8
            temp_combination = 5

        possible_combination, best_hand = quantities(self.cards)

        if possible_combination in [6,7]:
            self.cards = best_hand
            self.evaluation = possible_combination
            return possible_combination
        
        if temp_combination == 5:
            self.cards = f_cards
            self.evaluation = temp_combination
            return temp_combination
        
        if straight:
            self.cards = [s_cards[0]]
            for i in range(1, s_cards):
                if s_cards[i].rank_value != s_cards[i-1].rank_value:
                    self.cards.append(s_cards[i])
            self.evaluation = 4
            return 4
        
        self.cards = best_hand
        self.evaluation = possible_combination
        return possible_combination            
    
    def __gt__(self, other):
        if self == other:
            return self.tie_breaker(other) > 0
        return self.evaluation > other.evaluation
    
    def __lt__(self, other):
        if self == other:
            return self.tie_breaker(other) < 0
        return self.evaluation < other.evaluation
        
    def __eq__(self, other):
        return self.eval() == other.eval()
    
    def tie_breaker(self, other):
        match self.evaluation:
            case 9:
                return 0
            case 8 | 4 | 5 | 0:
                for i in range(5):
                    diff = self.cards[i].rank_value - other.cards[i].rank_value
                    if diff != 0:
                        return diff
                    return 0
            case _:
                quantity_self = dict()
                for card in self.cards:
                    if card.rank_value in quantity_self:
                        quantity_self[card.rank_value].append(card)
                    else:
                        quantity_self[card.rank_value] = [card]
                
                q_sorted_self = list(quantity_self.items())
                q_sorted_self.sort(key=lambda x: len(x[1]), reverse=True)
                
                quantity_other = dict()
                for card in other.cards:
                    if card.rank_value in quantity_other:
                        quantity_other[card.rank_value].append(card)
                    else:
                        quantity_other[card.rank_value] = [card]
                
                q_sorted_other = list(quantity_other.items())
                q_sorted_other.sort(key=lambda x: len(x[1]), reverse=True)   

                for i in range(len(q_sorted_self)):
                    diff = q_sorted_self[i][0] - q_sorted_other[i][0]
                    if diff != 0:
                        return diff
                return 0
                    
            