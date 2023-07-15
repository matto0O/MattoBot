from discord.ext import commands
import discord as dc
import asyncio
from cards import *
from players import *


class Game:
    def __init__(self, players, stack=5000, small_blind=50, big_blind=100):
        self.deck = Deck()
        self.temp_deck = self.deck
        self.pot = Pot()
        self.player_data = [Player(player[0], player[1][1]) for player in players]
        self.dealer_index = 0
        self.turn_index = 0
        self.sb = small_blind
        self.bb = big_blind

    def reset(self):
        self.temp_deck = self.deck

    async def announce(self, text):
        for player in self.player_data:
            await player.channel.send(text)

    def change_turn(self):
        self.turn_index = (self.turn_index + 1) % len(self.pot.players)

    async def deal(self):
        for _ in range(2):
            for player in (self.player_data):
                if player.status != PlayerStatus.BROKE:
                    card = self.temp_deck.get_random_card()
                    print(card)
                    with open(card[1], 'rb') as file:
                        img = dc.File(file)
                        player.hand.append(card)
                        await player.channel.send(file=img)

    async def play(self):
        await self.deal()
        self.pot = Pot(list(filter(lambda x: x.status==PlayerStatus.PLAYING,self.player_data)), self.sb + self.bb)
        sb = self.pot.players[self.dealer_index + 1]
        bb = self.pot.players[(self.dealer_index + 2) % len(self.pot.players)]

        sb.stack -= self.sb
        bb.stack -= self.bb
        self.turn_index = (self.dealer_index + 3) % len(self.pot.players)
        # self.announce()


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
            self.at_the_table[ctx.author] = (False, None)

    async def start(self):
        g = Game(self.at_the_table.items())
        await g.deal()

    # @commands.command()
    # async def spectate(self, ctx):
    #     await self.sit(ctx)
    #     pass

    @commands.command()
    async def ready(self, ctx):
        player = ctx.author
        server = self.client.guilds[0]

        category = dc.utils.get(server.categories, name='poker')

        channel_name=f"poker-{player.name}"
        channel = dc.utils.get(server.text_channels, name=channel_name)
        if not channel:
            overwrites = {
                server.default_role: dc.PermissionOverwrite(read_messages=False, view_channel=False),
                player: dc.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True),
                dc.utils.get(server.roles, name="BOT"): dc.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True)
            }
            channel = await server.create_text_channel(channel_name, category=category, overwrites=overwrites)

        self.at_the_table[player] = (True, channel)

        await channel.send("You are ready")

        if len(self.at_the_table) >= 2 and False not in list(map(lambda x: x[0], self.at_the_table.values())):
            await self.start()

    @commands.command()
    async def unready(self, ctx):
        channel = self.at_the_table[ctx.author][1]
        self.at_the_table[ctx.author] = (False, channel)
        if channel is not None:
            await channel.send("You are not ready")

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