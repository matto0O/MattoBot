from discord.ext import commands
import discord as dc
from photo_generator import generateCard
import asyncio
import os
from enum import Enum
import random

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
        self.cards = []

        
        folder_path = 'cards'
        files = os.listdir(folder_path)

        if not force_generate:
            jpg_files = [file for file in files if file.endswith('.jpg')]

            if len(jpg_files) == 52:
                try:
                    for rank in RANK_VALUES:
                        self.cards.append((f'{rank}s', f"cards/{rank}s.jpg"))
                        self.cards.append((f'{rank}d', f"cards/{rank}d.jpg"))
                        self.cards.append((f'{rank}h', f"cards/{rank}h.jpg"))
                        self.cards.append((f'{rank}c', f"cards/{rank}c.jpg"))
                    return
                except:
                    self.cards = []

        for filename in files:
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)

        for rank in RANK_VALUES:
            self.cards.append((f'{rank}s', generateCard(rank, 's', spade_clr)))
            self.cards.append((f'{rank}d', generateCard(rank, 'd', diamond_clr)))
            self.cards.append((f'{rank}h', generateCard(rank, 'h', heart_clr)))
            self.cards.append((f'{rank}c', generateCard(rank, 'c', club_clr)))

    def get_random_card(self):
        return self.cards.pop(random.randint(0,51))


class PlayerStatus(Enum):
    BROKE = 0
    FOLDED = 1
    ALL_IN = 2
    PLAYING = 3

class Player:
    def __init__(self, player, stack=5000):
        self.player = player
        self.stack = stack
        self.status = PlayerStatus.PLAYING
        self.hand = []

    def went_broke(self):
        self.status = PlayerStatus.BROKE

    def folded(self):
        self.status = PlayerStatus.FOLDED

    def all_in(self):
        self.status = PlayerStatus.ALL_IN

    def reset_status(self):
        self.status = PlayerStatus.PLAYING
        self.hand = []

class Game:
    def __init__(self, players, stack=5000, small_blind=50, big_blind=100):
        self.deck = Deck()
        self.temp_deck = self.deck
        self.pot = Pot()
        self.player_data = [Player(player) for player in players]

    def reset(self):
        self.temp_deck = self.deck

    async def deal(self, server):
        for i in range(2):
            for player in (self.player_data):
                if player.status != PlayerStatus.BROKE:
                    card = self.temp_deck.get_random_card()
                    print(card)
                    with open(card[1], 'rb') as file:
                        img = dc.File(file)
                        player.hand.append(card)
                        await dc.utils.get(server.text_channels, name=f"poker-{player.player.name}").send(file=img)

class Pot:
    def __init__(self, in_pot=[], total=0):
        self.players = in_pot
        self.total = total

class Poker(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.at_the_table = dict()

    async def sit(self, ctx):
        await ctx.author.move_to(self.client.guilds[0].voice_channels[-1])

    @commands.command(name="play-poker")
    async def play_poker(self, ctx):
        if len(self.at_the_table) == 8:
            # TODO say: too many players, you'll spectate
            await self.spectate(ctx)
        else:
            await self.sit(ctx)
            self.at_the_table[ctx.author] = False

    async def start(self, ctx):
        server = self.client.guilds[0]
        players = self.at_the_table.keys()
        category = dc.utils.get(server.categories, name='poker')
        for player in players:
            channel_name=f"poker-{player.name}"
            channel = dc.utils.get(server.text_channels, name=channel_name)
            if not channel:
                overwrites = {
                    server.default_role: dc.PermissionOverwrite(read_messages=False, view_channel=False),
                    player: dc.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True),
                    dc.utils.get(server.roles, name="BOT"): dc.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True)
                }
                channel = await server.create_text_channel(channel_name, category=category, overwrites=overwrites)

            # await channel.set_permissions(server.default_role, read_messages=False)
            # await channel.set_permissions(player, read_messages=True)
            # await channel.set_permissions(player, send_messages=True)
        g = Game(self.at_the_table.keys())
        await g.deal(server)

    @commands.command()
    async def test(self, ctx):
        g = Game([ctx.author])
        a = (self.at_the_table)
        print(a, type(a))
        for i in a:
            print(i, type(i))

    @commands.command()
    async def spectate(self, ctx):
        await self.sit(ctx)
        pass

    @commands.command()
    async def ready(self, ctx):
        self.at_the_table[ctx.author] = True
        if len(self.at_the_table) >= 2 and False not in self.at_the_table.values():
            await self.start(ctx)
        # TODO say: you are ready

    @commands.command()
    async def unready(self, ctx):
        self.at_the_table[ctx.author] = False
        # TODO say: you are not ready

    @commands.command()
    async def fold(self, ctx):
        pass

    @commands.command()
    async def check(self, ctx):
        pass

    @commands.command()
    async def call(self, ctx):
        pass

    @commands.command(name="raise")
    async def _raise(self, ctx):
        pass

    @commands.command(name="all-in")
    async def all_in(self, ctx):
        pass
        

def setup(client):
    asyncio.run(client.add_cog(Poker(client)))