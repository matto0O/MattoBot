from discord.ext import commands
import discord as dc
import asyncio
from .players import *
from .game_logic import *

class Poker(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.at_the_table = dict()
        self.game = None

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

    async def start(self, ctx):
        self.game = Game(self.at_the_table.items())
        await self.game.play(self.client)

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
            await self.start(ctx)

    @commands.command()
    async def unready(self, ctx):
        channel = self.at_the_table[ctx.author][1]
        self.at_the_table[ctx.author] = (False, channel)
        if channel is not None:
            await channel.send("You are not ready")

    @commands.command()
    async def fold(self, ctx):
        player = self.game.player_data[self.game.turn_index]
        try:
            self.game.turn_queue.remove(player)
            player.folded()
            self.game.pot.folded(player)
        except ValueError:
            await player.channel.send("You are not in the pot")

    @commands.command()
    async def check(self, ctx):
        pass

    @commands.command()
    async def call(self, ctx):
        player = self.game.player_data[self.game.turn_index]
        amount = self.game.pot.to_call(player)
        if player.stack < amount:
            return False
        player.stack -= amount
        self.game.pot.chip_in(player, amount)
        return True

    @commands.command(name="raise")
    async def _raise(self, ctx, amount):
        player = self.game.player_data[self.game.turn_index]
        if player.stack < amount:
            return False
        player.stack -= amount
        self.game.pot.chip_in(player, amount)
        return True

    @commands.command(name="all-in")
    async def all_in(self, ctx):
        player = self.game.player_data[self.game.turn_index]
        self.game.pot.chip_in(player, player.stack) 
        player.stack = 0
        player.status = PlayerStatus.ALL_IN
        

def setup(client):
    asyncio.run(client.add_cog(Poker(client)))