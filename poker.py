from discord.ext import commands
import discord as dc
from photo_generator import generateCard
import asyncio
import os

class Card:
    def __init__(self, rank, rank_value ,color):
        self.rank_value = rank_value
        self.rank = rank
        self.color = color
    
    def __eq__(self, other):
        return self.rank == other.rank

    def __gt__(self, other):
        return self.rank_value > other.rank_value
    
    def __lt__(self, other):
        return self.rank_value < other.rank_value

class Deck:
    def __init__(self, force_generate=False, spade_clr=(0,0,0,100), heart_clr=(199, 54, 44,100), diamond_clr=(34, 189, 132,100), club_clr=(145, 29, 124,100)):
        RANK_VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        self.spade_clr = spade_clr
        self.heart_clr = heart_clr
        self.diamond_clr = diamond_clr
        self.club_clr = club_clr
        self.cards = dict()

        
        folder_path = 'cards'
        files = os.listdir(folder_path)

        if not force_generate:
            jpg_files = [file for file in files if file.endswith('.jpg')]

            if len(jpg_files) == 52:
                try:
                    for rank in RANK_VALUES:
                        self.cards[f'{rank}s'] = f"/cards/{rank}s.jpg"
                        self.cards[f'{rank}d'] = f"/cards/{rank}d.jpg"
                        self.cards[f'{rank}h'] = f"/cards/{rank}h.jpg"
                        self.cards[f'{rank}c'] = f"/cards/{rank}p.jpg"
                    return
                except:
                    self.cards.clear()

        for filename in files:
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)

        for rank in RANK_VALUES:
            self.cards[f'{rank}s'] = generateCard(rank, 's', spade_clr)
            self.cards[f'{rank}d'] = generateCard(rank, 'd', diamond_clr)
            self.cards[f'{rank}h'] = generateCard(rank, 'h', heart_clr)
            self.cards[f'{rank}c'] = generateCard(rank, 'c', club_clr)

class Poker(commands.Cog):
    def __init__(self, client):
        pass

    @commands.command()
    async def card(self, ctx):
        Deck()

def setup(client):
    asyncio.run(client.add_cog(Poker(client)))