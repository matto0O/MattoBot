import discord as dc
from discord.ext import commands
import music
import football
import fm
import poker_files.poker as poker

client = commands.Bot(command_prefix='!', intents=dc.Intents.all())

cogs = [music, football, fm, poker]

for i in range(len(cogs)):
    cogs[i].setup(client)


@client.event
async def on_ready():
    print('Siema. Jestem {0.user}'.format(client))

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is not None and len(before.channel.members) == 1 and before.channel.members[0].bot:
        try:
            await before.channel.members[0].move_to(None)
        except:
            pass    

@client.event
async def on_presence_update(before, after):
    this_guild = client.guilds[0]
    gajs_role = dc.utils.find(lambda r: r.name == 'gajs', this_guild.roles)
    gajs = []
    for user in client.get_all_members():
        if gajs_role in user.roles:
            gajs.append(user)
    # edlg = dc.utils.find(lambda c: c.name == 'Estadio De La Gruz', this_guild.channels)
    # if set(gajs) <= set(edlg.members):
    #     # TODO change privacy
    #     pass
    # else: 
    #     pass 
    if after in gajs:      
        for user in gajs:
            if user.status not in [dc.Status.online, dc.Status.idle]:
                return   
        ll2 = dc.utils.find(lambda c: c.name == 'la-liga2', this_guild.channels)
        #await ll2.send(f"{gajs_role.mention} wszyscy som chodzcie grac")           
    

with open(R"C:\Users\mateu\dc_bot\tokens") as file:
    client.run(file.readline()) 