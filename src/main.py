# Discord python bot for Konziis!
# 
# Python discord bot:
#   https://realpython.com/how-to-make-a-discord-bot-python/
#   https://discordpy.readthedocs.io/en/latest/index.html
#   https://github.com/Rapptz/discord.py/tree/v1.7.2/examples
# 
# Wolfram-API:
#   https://products.wolframalpha.com/api/documentation/#getting-started

import os
import random
import asyncio
from socket import socket

import discord
from discord import activity 
from discord.ext import commands
from discord.ext import tasks
from dns.rcode import NOERROR
import requests

from mcstatus import MinecraftServer
import wolframalpha

# DEBUG:

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
WOLFRAM_APPID = os.getenv('WOLFRAM_APPID')

MC_SERVER_CHECK_TIME = 10 * 60
MC_SERVER_ADDRESS = "ratius99.aternos.me"
MC_SERVER_STATUS_INT = 0

MESSAGE_CHANNEL = "📯mitteilungen"
TXT_VOICE_UPDATE = ["is needy and wait's for academic trash talk", 
                    "is lonely and want's to talk", 
                    "is waiting for you ",
                    "is sitting alone here",
                    "<put here some random text stuff>"
                    ]

basic_activity_name =" in der Cloud! ☁"
bot = commands.Bot(command_prefix="!", activity= discord.Game(name=basic_activity_name))

wolframclient = wolframalpha.Client(WOLFRAM_APPID)

# Helper

def json_extract(obj, key):
    """Recursively fetch values from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    values = extract(obj, arr, key)
    return values

# Initialization errors

if not (TOKEN and GUILD and WOLFRAM_APPID):
    raise RuntimeError("Missing environmental variable.")

# Tasks

@tasks.loop(minutes=10)
async def check_mc_status():
    print("loopmc")

    mc_status = basic_activity_name
    players = 0
    
    try:
        server = MinecraftServer.lookup(MC_SERVER_ADDRESS)
        status = server.status()
        players = status.players.online
    except ConnectionRefusedError:
        mc_status = " mit Errors ..."
    except Exception:
        mc_status = " mit \"bad status error\" :-("

    # if no error happend:
    if (players):
        mc_status = " mit "+("einem Spieler" if (players==1) else str(players)+" Spielern")+" MC!"

    await bot.change_presence(activity = discord.Game(name=mc_status))

# Events

@bot.event 
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        channel_name=after.channel.name
        print("lonely state")
        await asyncio.sleep(10) # wait to est if user is shy / has misclicked
        if after.channel is not None:
            print("trigger")
            guild = discord.utils.get(bot.guilds, name=GUILD)
            voice_channel = discord.utils.get(guild.voice_channels, name=channel_name)
            print(voice_channel.voice_states)
            if len(voice_channel.voice_states)==1:
                print("t2")
                text_channel = discord.utils.get(guild.text_channels, name=MESSAGE_CHANNEL)
                await text_channel.send(f"Moin! {member.name} "+random.choice(TXT_VOICE_UPDATE)+". Visit him at #"+after.channel.name+".")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    check_mc_status.start()

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, hier ist der nerfffiger Diiscordbot aus Konziis!'
    )

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    #read messageses   
    await bot.process_commands(message)

# Commands

@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    print("roll event!")
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    print(dice)
    await ctx.send(', '.join(dice))

@bot.command(name='hi', help='Say \"Hi!\" multiple times.')
async def roll(ctx, number_of_hi: int = 1):
    print("hi!")
    for _ in range(number_of_hi):
        await ctx.send('Hi!')

@bot.command(name='echo', help='Echo string.')
async def roll(ctx, *, txt:str):
    print("echo!")
    await ctx.send(txt)

@bot.command(name='emoji', help='Creates custom server emoji.')
async def roll(ctx, emoji_name: str, image_url:str):
    print("emoji!")
    response = requests.get(image_url)
    img = response.content   
    img = await ctx.guild.create_custom_emoji(name=emoji_name, image=img)
    await ctx.send(">> Emoji created: "+str(img))

@bot.command(name='molec', help='Visualize a given molecule string. Supports MIME and other structural identifier. Note: Triple bonds in SMILES strings represented by \'\#\' have to be URL-escaped as \'%23\' and \'?\' as \'%3F\'. ', brief='Visualize a given molecule string.')
async def roll(ctx, smile_string: str):
    print('molec!')
    url1 = 'http://cactus.nci.nih.gov/chemical/structure/' + smile_string+ '/image'
    await ctx.send(">> Molecule: "+ str(url1))
    
@bot.command(name='wolfram', help='Use wolfram-api. It can do everything WolframAlpha can do: Equations, Weather  (Overview: https://www.wolframalpha.com/)', brief='Use Wolfram Alpha to solve Math or ask random stuff.')
async def roll(ctx, *, question_string: str):
    print('wolfram! '+ question_string)
    res = wolframclient.query(question_string)
    if not res.success:
        await ctx.send(">> Wolfram Weisnisch Weiter... ")

    #pods = res.pod
    #if len(res_objects) == 0:
    #    await ctx.send(">> Wolfram: No Images found.")
    #await ctx.send(">> Wolfram: "+ str(next(res.results).text))

@bot.command(name='wolfram-img')
async def roll(ctx, *, question_string: str):
    """First. Second. Long... ......... ............. ........ ........
    newline ...... ....... .......... ......"""

    print('wolfram-img! ' + question_string)
    res = wolframclient.query(question_string)
    if not res.success:
        await ctx.send(">> Wolfram Weisnisch Weiter... ")
    
    subpods = json_extract(res, "subpod")
    if len(subpods) == 0:
        await ctx.send(">> Wolfram: No Images found.")

    message = " "
    for subpod in subpods:
        message += " " + subpod.img.src

    await ctx.send(">> Wolfram: "+ message)

@bot.event
async def on_command_error(ctx, error):
    print(error.__cause__)
    await ctx.send(">> Error: "+str(error.__cause__))

bot.run(TOKEN)


# Custom event example:
# 
# bot.dispatch("custom_event", arg1, arg2)
#
# @bot.event
# async def on_custom_event(arg1, arg2):
#     print("Custom event")
