import discord as dc
from discord.ext import commands
import music

client = commands.Bot(command_prefix='!', intents=dc.Intents.all())

cogs = [music]

for i in range(len(cogs)):
    cogs[i].setup(client)


@client.event
async def on_ready():
    print('Siemafsad. Jestem {0.user}'.format(client))

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is not None and len(before.channel.members) == 1 and before.channel.members[0].bot:
        try:
            await before.channel.members[0].move_to(None)
        except:
            pass    


with open(R"C:\Users\mateu\dc_bot\token") as file:
    client.run(file.readline())
