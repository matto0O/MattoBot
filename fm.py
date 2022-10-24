from discord.ext import commands
import discord as dc
from prettytable import PrettyTable
import asyncio
import fnmatch
from operator import itemgetter
from logs import log

class Player:
    def __init__(self, user):
        self.name = str(user)
        self.mention = user.mention
        self.games = 0
        self.wins = 0
        self.draws = 0    
        self.losses = 0
        self.gf = 0
        self.ga = 0

    def played(self, result, home):
        self.games += 1
        score = result.split(':')
        if int(score[home]) < int(score[(home+1)%2]):
            self.wins += 1
        elif int(score[home]) == int(score[(home+1)%2]):       
            self.draws += 1
        else:
            self.losses += 1
        self.gf += int(score[(home+1)%2])
        self.ga += int(score[home])          

class Fm(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.has_role('gajs')
    @commands.command()
    async def result(self, ctx, *args):
        try:
            if len(args) != 4:
                print("Invalid amount of arguments")
                raise ValueError
            with open("results.txt", "a", encoding="UTF-8") as file:
                if len(fnmatch.filter(args[:-2], '<*>')) != 2 or not\
                set(args[:-2]).issubset(set([user.mention for user in ctx.guild.members])):
                    print("Invalid host/visitor tag")
                    raise ValueError
                split = args[2].split(':')
                if len(split) != 2:
                    print("Invalid result")
                    raise ValueError
                int(split[1])
                int(split[0])     
                file.write("{} {} {}\n".format(args[0], args[1], args[2]))
        except (ValueError, IndexError):
            await ctx.send("Chłopie, zły format\n@Gospodarz @gość wynik sezon\nPrzykład: @matto @warblade7 2:1 2022/23")
        except Exception as e:
            log("fm.result", args, e)

    @commands.has_role('gajs')            
    @commands.command()
    async def h2h(self, ctx, *args):
        try:
            if len(args) != 2:
                print("Invalid amount of arguments")
                raise ValueError
            with open("results.txt", "r", encoding="UTF-8") as file:
                if len(fnmatch.filter(args, '<*>')) != 2 or not\
                set(args).issubset(set([user.mention for user in ctx.guild.members])):
                    print("Invalid host/visitor tag")
                    raise ValueError
                w = 0
                d = 0
                l = 0
                g1 = 0
                g2 = 0 
                for game in file.readlines():
                    split = game.split(' ')
                    if split[0] == args[0] and split[1] == args[1]:
                        result = split[-2].split(':')
                        g1 += int(result[0])
                        g2 += int(result[1])
                        if int(result[0]) > int(result[1]):
                            w += 1
                        elif int(result[0]) == int(result[1]):
                            d += 1
                        else:
                            l += 1         
                    elif split[1] == args[0] and split[0] == args[1]:
                        result = split[-2].split(':')
                        g2 += int(result[0])
                        g1 += int(result[1])
                        if int(result[0]) > int(result[1]):
                            l += 1
                        elif int(result[0]) == int(result[1]):
                            d += 1
                        else:
                            w += 1  
            await ctx.send("{}: wygrał {} gier, przy {} zdobytych golach\nPadło {} remisów\n{}: wygrał {} gier, przy {} zdobytych golach".format(args[0], w, g1, d, args[1], l, g2))            
        except (ValueError):
            await ctx.send("Chłopie, zły format\n@Gospodarz @gość\nPrzykład: @matto @warblade7")
        except Exception as e:
            log("fm.h2h", args, e)    

    @commands.has_role('gajs')
    @commands.command()
    async def games(self, ctx, *args):
        try:
            if len(args) not in [1, 2]:
                print("Invalid amount of arguments")
                raise ValueError
            with open("results.txt", "r", encoding="UTF-8") as file:
                if len(fnmatch.filter(args, '<*>')) == len(args) and set(args).issubset(set([user.mention for user in ctx.guild.members])):
                    for game in file.readlines():
                        split = game.split(' ')
                        if len(args) == 1 and args[0] in split:
                            await ctx.send(game)
                        elif (split[0] == args[0] and split[1] == args[1]) or (split[1] == args[0] and split[0] == args[1]):
                            await ctx.send(game)
                else:
                    print("Invalid host/visitor tag")
                    raise ValueError        
        except ValueError:
            await ctx.send("Chłopie, zły format\n@gospodarz @gość\nPrzykład: @matto @warblade7\nlub: @gracz")      
        except Exception as e:
            log("fm.games", args, e)

    @commands.has_role('gajs')
    @commands.command()
    async def direct(self, ctx):
        stats = dict()
        gajs_role = dc.utils.find(lambda r: r.name == 'gajs', ctx.guild.roles)
        gajs = []
        for user in ctx.guild.members:
            if gajs_role in user.roles:
                gajs.append(user)
        for user in gajs:
            stats[user.mention] = Player(user)
        with open("results.txt", "r", encoding="UTF-8") as file:
            for game in file.readlines():
                split = game.split(' ')
                stats[split[0]].played(split[2], True)
                stats[split[1]].played(split[2], False)
        com = PrettyTable(['.', "{:25s}".format("Nick"), 'PTS', 'GP', 'P/G', 'W', 'D', 'L', 'GF', 'GA', 'GD'])
        for player in gajs:
            x = stats[player.mention]
            stats[player.mention] = [x.mention, x.wins*3 + x.draws, x.games, 0 if x.games==0 else round((x.wins*3 + x.draws)/x.games, 2), x.wins, x.draws, x.losses, x.gf, x.ga, x.gf - x.ga]
        for enum, x in enumerate(sorted(stats.values(), key=itemgetter(1, 3, 9, 7, 0), reverse=True)):
            com.add_row([enum+1] + x) 
        await ctx.send(com)    
        except Exception as e:
            log("fm.direct", '', e)

def setup(client):
    asyncio.run(client.add_cog(Fm(client)))   