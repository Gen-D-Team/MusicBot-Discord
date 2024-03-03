import discord
from discord.ext import commands
from pytube import YouTube
import time

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

discord_token = "MTE2MDQxNTQyNDY0MzYxMjcxMw.Gam7HM.LalRhatrCWqfejfi8rPrKNhIFxatU51UsD8-Jw"

@bot.command()
async def play(ctx, url):
    # Check if user is join into channel or not
    if ctx.author.voice is None:
        await ctx.send("You're not in a voice channel. Please connect to a voice channel")
    else:
        channel = ctx.author.voice.channel

        if ctx.voice_client is None:
            vc = await channel.connect()
        else:
            if ctx.voice_client.channel != channel:
                await ctx.voice_client.disconnect()
                vc = await channel.connect()
            else:
                vc = ctx.voice_client

        #filter out the url then take the stream
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc()
        
        # check if audio stream work properly
        if audio_stream:
            best_audio = audio_stream.first()
            audio_url = best_audio.url
            vc.play(discord.FFmpegPCMAudio(audio_url, options="-vn", before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 4'), after=lambda e: play_next(ctx))
            
            # show duration of audio stream
            duration_seconds = int(yt.length)
            duration_minutes = duration_seconds // 60
            duration_seconds %= 60
            await ctx.send(f"Now playing: {yt.title} | Duration: {duration_minutes}m {duration_seconds}s")

            print("Now playing: " + yt.title)
        else:
            print("No audio stream found for the given URL.")

# Create an Array for add queue
add_to_queue = []

# Add a song to queue
@bot.command()
async def add(ctx, url):
    add_to_queue.append(url)
    await ctx.send(f'"{url}" added to queue')

# Play the next song in the queue
def play_next(ctx):
    if len(add_to_queue) > 0:
        next_song = add_to_queue.pop(0)
        bot.loop.create_task(play(ctx, next_song))

# Just on or off of the loop command
mode = ["on", "off"]


@bot.command()
async def loop(ctx, mode: str):
    if ctx.voice_client is None:
        vc = await ctx.author.voice.channel.connect()
    else:
        vc = ctx.voice_client

    def play_again():
        vc.play(discord.FFmpegPCMAudio(source="music.mp3"), after=lambda e: play_again())

    if mode == "on":
        await ctx.send("Now Looping!")
        play_again()
    elif mode == "off":
        await ctx.send("No longer Looping!")
        return

# Skip the current song and play the next song if it exists
@bot.command()
async def skip(ctx):
    if len(add_to_queue) > 0:
        await ctx.send("Skipping and play the next song")
        ctx.voice_client.stop()
        play_next(ctx)
    else:
        await ctx.send("There is no song in the queue")

# Pause the current song
@bot.command()
async def pause(ctx):
    ctx.voice_client.pause()
    await ctx.send("The Track Has Stopped")

# Continue playing the current song
@bot.command()
async def resume(ctx):
    ctx.voice_client.resume()
    await ctx.send("Resuming The Track")

# The bot will leave voice call
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("I left the voice channel")

# Simply helpme message
@bot.command()
async def helpme(ctx):
    message = """
```
Available Commands:
!helpme - Show all available commands
!play <url> - Play music and another song to queue
!add <url> - Add song to the queue
!skip - Skip the current song
!loop on/off - Loop current song but you have to wait current song to loop
!resume - Resume playing the song
!pause - Pause the song currently playing
!leave - Leave the voice channel
```
"""
    await ctx.send(message)

# Check if the bot is ready or not
@bot.event
async def on_ready():
    print("Ready!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!helpme"))

# Show what room does bot connect
@bot.event
async def on_voice_state_update(member, before, after):
    print(f"Voice state updated: {before.channel} -> {after.channel}")



bot.run(discord_token)
