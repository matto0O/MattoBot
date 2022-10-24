from discord.ext import commands
import requests
import asyncio
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from logs import log

class Football(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def standings(self, ctx, *args):
        try:
            com =   "{} -> {}\n".format("Dostępna liga", "Komenda") +\
                                "=====================\n" +\
            "{} -> {}\n".format("Premier League", "!standings pl") +\
            "{} -> {}\n".format("La Liga", "!standings la") +\
            "{} -> {}\n".format("La Liga2", "!standings la2") +\
            "{} -> {}\n".format("Serie A", "!standings sa") +\
            "{} -> {}\n".format("Serie B", "!standings sb") +\
            "{} -> {}\n".format("Bundesliga", "!standings bu") +\
            "{} -> {}\n".format("Ligue 1", "!standings l1") +\
            "{} -> {}\n".format("Liga Portugal", "!standings lp") +\
            "{} -> {}\n".format("Ekstraklasa", "!standings esa")
            if len(args) == 1:
                response = ""
                match args[0]:
                    case "pl":
                        response = requests.get("https://www.soccerstats.com/latest.asp?league=england").text
                    case "la":
                        response = requests.get("https://www.soccerstats.com/latest.asp?league=spain").text
                    case "la2":
                        response = requests.get("https://www.soccerstats.com/latest.asp?league=spain2").text
                    case "sa":
                        response = requests.get("https://www.soccerstats.com/latest.asp?league=italy").text
                    case "sb":
                        response = requests.get("https://www.soccerstats.com/latest.asp?league=italy2").text
                    case "bu":
                        response = requests.get("https://www.soccerstats.com/latest.asp?league=germany").text
                    case "l1":
                        response = requests.get("https://www.soccerstats.com/latest.asp?league=france").text
                    case "lp":
                        response = requests.get("https://www.soccerstats.com/latest.asp?league=portugal").text
                    case "esa":
                        response = requests.get("https://www.soccerstats.com/latest.asp?league=poland").text
                    case _:
                        await ctx.send(com)
                        return
                soup = BeautifulSoup(response, 'lxml')
                f = open("league_request.txt", "w", encoding="utf-8")
                table = soup.find('table', cellpadding="2", cellspacing="0", id="btable", width="100%")
                splitter = "\n\n\n============\n\n\n"
                for team in table.find_all(itemtype="http://schema.org/SportsTeam"):
                    f.write('\r'.join(line for line in team.text.splitlines() if line))
                    f.write(splitter)
                f.close()
                with open("league_request.txt", encoding="utf-8") as results:
                    com = PrettyTable(['.', "{:25s}".format("TEAM"), 'PTS', 'GP', 'W', 'D', 'L', 'GF', 'GA', 'GD'])
                    for team in results.read().split(splitter)[:-1]:
                        details = team.replace("\xa0", "").split('\n')
                        com.add_row([details[0], details[1], details[9], details[2], details[3], details[4], details[5], details[6], details[7], details[8]]) 
            await ctx.send(com)
        except Exception as e:
            log("football.standings", args, e)                   

def setup(client):
    asyncio.run(client.add_cog(Football(client)))   