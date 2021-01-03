import discord
import datetime
import mysql.connector
import aiohttp
import json
import os
from discord.ext import commands, tasks
from steam.steamid import SteamID
from discord.utils import get
from colorama import init, Fore

init()

giveaway_ban_role_name = 'Giveaway Ban'
giveaway_role_name = 'Giveaway Member'
vip_role_name = 'VIP'

class Administrator(commands.Cog):
    """ Administrator Commands """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{Fore.RED}Administrator cog Ready!')

    @commands.command(aliases=['gban'], description='Ban a member for participating to giveaway', help='giveawayban [user]')
    @commands.has_permissions(manage_roles=True)
    async def giveawayban(self, ctx, user: discord.Member):
        embed = discord.Embed(color=discord.Color.red())
        role = get(user.guild.roles, name=giveaway_ban_role_name)
        await user.add_roles(role)
        role = get(user.guild.roles, name=giveaway_role_name)
        for role in user.roles:
            if role.name == giveaway_ban_role_name:
                embed.description = f"{user.mention} is already banned from Giveaway!"
                await ctx.send(embed=embed)
                return


        await user.remove_roles(role)
        embed.description = f"{user.mention} has been banned from Giveaway"
        await ctx.send(embed=embed)

    @commands.command(aliases=['gunban'], description='Unban a member for participating to giveaway', help='giveawayunban [user]')
    @commands.has_permissions(manage_roles=True)
    async def giveawayunban(self, ctx, user: discord.Member):
        embed = discord.Embed(color=discord.Color.red())
        banned = False
        for role in user.roles:
            if role.name == giveaway_ban_role_name:
                banned = True
        if banned == False:
            embed.description = f"{user.mention} is not banned from Giveaway."
        else:
            role = get(user.guild.roles, name=giveaway_ban_role_name)
            await user.remove_roles(role)
            embed.description = f"{user.mention} has been unbanned from Giveaway"
        await ctx.send(embed=embed)

    @commands.command(aliases=['sp'], description='Set command prefix', help='setprefix (prefx)')
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx, prefix = 'tf2 '):

        with open(f"./json/bot.json", 'r') as file: # Get Bot Token
            bot_info = json.load(file)

        description = f"Prefix changed to **`{prefix}`**\nType **`{prefix} help`**"

        await ctx.send(embed = discord.Embed(description = description, color = discord.Color.gold()))
        bot_info["prefix"] = prefix
        with open(f"./json/bot.json", 'w') as file: # Get Bot Token
            json.dump(bot_info, file, indent=1)

def setup(client):
    client.add_cog(Administrator(client))
