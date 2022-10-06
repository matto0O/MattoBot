import queue
import time

import discord
from discord.ext import commands
import youtube_dl
from threading import Thread
import threading


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
        self.callback_queue = queue.Queue()

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("Bruv... join a channel!")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        elif ctx.voice_client.is_playing():
            await ctx.send("Sorry, I'm busy!")
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.command()
    async def stop(self, ctx):
        if ctx.author.voice.channel is not ctx.voice_client.channel or not ctx.voice_client.is_playing:
            await ctx.send("Nothing to stop")
        else:
            ctx.voice_client.stop()

    @commands.command()
    async def dc(self, ctx):
        if ctx.voice_client is not None and ctx.author.voice.channel == ctx.voice_client.channel:
            self.queue.empty()
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("You can't disconnect the bot while not on its channel!")

    async def play_dc(self, ctx):
        if self.queue.size() > 0:
            await self.play(ctx, self.queue.dequeue())
        else:
            await self.dc(ctx)

    def check_for_next(self, ctx):
        while ctx.voice_client.is_playing():
            pass
        self.callback_queue.put(self.play_dc)

    @commands.command()
    async def play(self, ctx, url):
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 3',
                          'options': '-vn'}
        YDL_OPTIONS = {'format': "bestaudio"}
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            await self.join(ctx)
            vc = ctx.voice_client
            vc.play(source)
            # player = Thread(target=vc.play, args=(source,))
            # player.start()
            # checker = Thread(target=self.check_for_next, args=(ctx,))
            # checker.start()
            # while True:
            #     try:
            #         callback = self.callback_queue.get(False)
            #         break
            #     except queue.Empty:
            #         print("check")
            # await callback(ctx)

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
            "https://youtu.be/3dHpEfmegOA" # harnaś ice tea
        ]
        comms = [
            "Gdzie jest głośnik?!",
            "Ale mam esse :cowboy: :call_me: ",
            "Tam nikogo nie ma",
            "Ktoś zajebał misclicka",
            "Z A M K N I J  R Y J"
        ]
        await ctx.send(random.choice(comms))
        await self.play(ctx, random.choice(songs))


def setup(client):
    import asyncio
    asyncio.run(client.add_cog(Music(client)))
