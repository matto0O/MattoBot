import discord as dc
from discord.ext import commands
import music

client = commands.Bot(command_prefix='!', intents=dc.Intents.all())

cogs = [music]

for i in range(len(cogs)):
    cogs[i].setup(client)


@client.event
async def on_ready():
    print('Siema. Jestem {0.user}'.format(client))


# @client.event
# async def on_message(message):
#     print(message.content)
#     if message.author == client.user:
#         return
#     if message.content.startswith('!hello'):
#         await message.channel.send('Hello!')

with open("token") as file:
    client.run(file.readline())
