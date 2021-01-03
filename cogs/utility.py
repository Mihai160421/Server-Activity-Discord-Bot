import discord
import datetime
import json
import asyncio
from discord.ext import commands, tasks
from colorama import init, Fore
# !from jishaku.functools import executor_function


init() # Initiate colorama module



def get_cog_emoji_prefix(cog):
    if cog == 'Utility':
        return ':wrench:'
    elif cog == 'Activity':
        return ':video_game:'
    elif cog == "Administrator":
        return ':no_entry:'
    else:
        return ""

start_date = datetime.datetime.now()


# !@executor_function
def load_json(json_path):
    with open(json_path, 'r') as file:
        return json.load(file)



class Utility(commands.Cog):
    """```\nUtility Commands\n```"""
    def __init__(self, client):
        self.client = client
        self.client.remove_command('help')


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{Fore.RED}Utility cog ready!")


    @commands.command(aliases = ['hp', 'halp'], description = 'Show Help message.', help = 'help')
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def help(self, ctx, category = None):
        administrator_require = False
        client_commands = self.client.commands
        client_cogs = self.client.cogs
        client_name = self.client.user.name
        commands_name = [c.name for c in client_commands]
        cogs_name = [c.lower() for c in client_cogs]
        embed = discord.Embed(title=f"{client_name} Command list.")
        if category == None:
            administrator_require = True
            for cog in client_cogs:
                if not cog.startswith("_") and cog != 'Administrator':
                    name_prefix = get_cog_emoji_prefix(cog)
                    embed.add_field(name=f'{name_prefix} {cog}', value=f'**`{ctx.prefix}help {cog.lower()}`**', inline=True)

        elif category in cogs_name:
            cog = self.client.get_cog(category.title())
            embed.description = cog.__doc__
            name_prefix = get_cog_emoji_prefix(category.title())
            commands_list = cog.get_commands()
            value = '**`' + '`** **`'.join(c.name for c in commands_list) + '`**'
            embed.add_field(name=f'{name_prefix} {category.title()} Commands List:', value=value)
            embed.set_footer(text=f'Type {ctx.prefix}help [command] (without "[]")')
        elif category in commands_name:
            command = self.client.get_command(category)
            aliases = ", ".join(command.aliases)
            embed.add_field(name='Description:', value=f"`{command.description}`", inline=False)
            embed.add_field(name='Usage:', value=f"`{ctx.prefix}{command.help}`", inline=False)
            embed.add_field(name='Aliases:', value=f"`{aliases}`", inline=False)
        else:
            await ctx.send("Sorry but i could not find that command.")
            return
        if administrator_require:
            name_prefix = get_cog_emoji_prefix('Administrator')
            embed.add_field(name=f'{name_prefix} Administrator', value=f'**`{ctx.prefix}help administrator`**', inline=True)
        embed.set_footer(text=f"Thanks for using {client_name}. We have a total of {len(commands_name)} commands.")
        await ctx.send(embed=embed)

    @commands.command(aliases=['si'], description='Get informations about the server', help='serverinfo')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def serverinfo(self, ctx):
        guild = ctx.guild
        created_date = guild.created_at.ctime()
        region = str(guild.region).title()
        embed = discord.Embed(description=guild.description)
        embed.set_author(name=f'{guild.name}', icon_url=guild.icon_url)
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name='ID', value=f'{guild.id}', inline=False)
        embed.add_field(name='Owner', value=f'{guild.owner}', inline=False)
        embed.add_field(name='Members:', value=f'{guild.member_count}', inline=False)
        embed.add_field(name='Created at', value=created_date, inline=False)
        embed.add_field(name='Active invites', value=len(await guild.invites()), inline=False)
        embed.add_field(name='Members Banned', value=len(await guild.bans()), inline=False)
        embed.add_field(name='Roles Count', value=len(guild.roles), inline=False)
        embed.add_field(name='Premium Members', value=guild.premium_subscription_count, inline=False)
        embed.add_field(name='Voice Channels', value=len(guild.voice_channels), inline=False)
        embed.add_field(name='Text Channles', value=len(guild.text_channels), inline=False)
        embed.add_field(name='Categories', value=len(guild.categories), inline=False)
        embed.add_field(name='Total Channels', value=len(guild.channels), inline=False)
        embed.add_field(name='Verification Level', value=guild.verification_level, inline=False)
        embed.add_field(name='Mfa Level', value='Yes' if guild.mfa_level == 1 else 'No', inline=False)
        embed.add_field(name='Emoji list', value=len(guild.emojis), inline=False)
        embed.add_field(name='Region', value=region, inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=[], descrption='Get the user discord id', help='id (user)')
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def id(self, ctx, user : discord.Member = None):
        if user == None or ctx.author == user:
            await ctx.send(f"{ctx.author.name}, your discord id is **{ctx.author.id}**")
        else:
            await ctx.send(f"{ctx.author.name}, {user.name} discord id is **{user.id}**")

    @commands.command(aliases=[], description='Get Github Link', help='github')
    async def github(self, ctx):
        await ctx.send('https://github.com/Mihai160421/TF2-Romania-Discord-Bot')

def setup(client):
    client.add_cog(Utility(client))
