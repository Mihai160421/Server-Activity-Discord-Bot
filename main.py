#   Discord Bot for TF2 Romania
#   Python Verison 3.9.1
#   Discord Py Version 1.5.1
#   Author: Mihái#0001   (Discord) / DiscordID : 468179605124153344
#   Github : https://github.com/Mihai160421/TF2-Romania-Discord-Bot


import discord
import os
import json
from pydactyl import PterodactylClient
from discord.ext import commands
from colorama import init, Fore


init() # Initiate colorama

TOKEN = ''

with open("./json/bot.json", 'r') as file:
    TOKEN = json.load(file)["token"]

def get_prefix(client, message):
    with open("./json/bot.json", 'r') as file:
        return json.load(file)["prefix"]

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=get_prefix , intents=intents)


@client.event
async def on_ready():
    with open("./json/bot.json", 'r') as file:
        DEFAUL_PREFIX = json.load(file)["prefix"]
    print(f"{Fore.RED}{client.user} is online!")
    activity = discord.Game(name=f"{DEFAUL_PREFIX}help", type=3)
    await client.change_presence(status=discord.Status.online, activity=activity)


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')


client.run(TOKEN)
