import discord as dc
import asyncio
from discord.ext import commands
import youtube_dl
from youtube_search import YoutubeSearch


class SoundQueue:
    def __init__(self):
        self.q = []

    def enqueue(self, elem):
        self.q.append(elem)

    def dequeue(self):
        try:
            return self.q.pop(0)
        except IndexError:
            return None

    def size(self):
        return len(self.q)

    def empty(self):
        self.q.clear()


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = SoundQueue()

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("Gdzie jest głośnik?!")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
            self.queue.empty()
        elif ctx.voice_client.is_playing():
            await ctx.send("Z A M K N I J  R Y J")
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.command()
    async def stop(self, ctx):
        if ctx.author.voice.channel is not ctx.voice_client.channel or not ctx.voice_client.is_playing:
            await ctx.send("Tam nikogo nie ma")
        else:
            ctx.voice_client.stop()

    @commands.command()
    async def dc(self, ctx):
        if ctx.voice_client is not None and ctx.author.voice.channel == ctx.voice_client.channel:
            self.queue.empty()
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("Z A M K N I J  R Y J")

    def run(self, ctx, src):
        ctx.voice_client.play(src, after=(lambda x=None: self.check_for_next(ctx)))      

    def check_for_next(self, ctx):
        if self.queue.size() > 0:
            asyncio.run(self.play(ctx, self.queue.dequeue()))

    @commands.command()
    async def play(self, ctx, url, *args):
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 3',
                          'options': '-vn'}
        YDL_OPTIONS = {'format': "bestaudio", 'noplaylist':'True'}
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(url, download=False)  
            except youtube_dl.utils.DownloadError:
                if len(args) == 0:
                    args = []  
                new_url = "https://www.youtube.com{}".format(YoutubeSearch(url + ' '.join(args), max_results=1).to_dict()[0]["url_suffix"])
                info = ydl.extract_info(new_url, download=False)     
            finally:
                await ctx.send("Teraz leci: \n{}".format(info["title"]))
                url2 = info['formats'][0]['url']
                source = await dc.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                await self.join(ctx)
                self.run(ctx, source)

    @commands.command()
    async def add(self, ctx, url):
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await self.play(ctx, url)
        else:
            self.queue.enqueue(url)

    @commands.command()
    async def essa(self, ctx):
        import random
        songs = [
            "https://www.youtube.com/watch?v=Sug433bP-mw", # impreza
            "https://www.youtube.com/watch?v=xm_ujA1CXCc", # testarossa
            "https://www.youtube.com/watch?v=iewMEY-66yw", # kokaina
            "https://youtu.be/3dHpEfmegOA", # harnaś ice tea
            "https://youtu.be/i92EzcnOMJY" # bandyta
        ]
        comms = [
            "Ale mam esse :cowboy: :call_me: ",
            "Ktoś zajebał misclicka",
            "Ogarniemy stary :sunglasses: ",
        ]
        await ctx.send(random.choice(comms))
        await self.play(ctx, random.choice(songs))


def setup(client):
    asyncio.run(client.add_cog(Music(client)))
