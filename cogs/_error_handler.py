import discord
from discord.ext import commands, tasks
from colorama import init, Fore

init() # Initiate colorama module

class _ErrorHandler(commands.Cog):
    """ Error Handler Cog """
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{Fore.RED}ErrorHandler Cog ready!")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed = discord.Embed(description = "Please pass in all required arguments.", color = discord.Color.red()))
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(embed = discord.Embed(description = "This command does not exist.", color = discord.Color.red()))
        elif isinstance(error, commands.BadArgument):
            await ctx.send(embed = discord.Embed(description = "Bad Argument", color = discord.Color.red()))
        elif isinstance(error, commands.CommandOnCooldown):
            time = f"{round(error.retry_after) // 60} minutes" if error.retry_after >= 60 else f"{round(error.retry_after)} seconds."
            await ctx.send(embed = discord.Embed(description = f"This command is on cooldown. Try again in {time}", color = discord.Color.red()))
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(embed = discord.Embed(description = f"I don't have permission to do that. Missing Permissions: {error.missing_perms}", color = discord.Color.red()))
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(embed = discord.Embed(description = f"Member not found.", color = discord.Color.red()))
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed = discord.Embed(description = f"You don't have permission to do that. Missing Permissions: {error.missing_perms}", color = discord.Color.red()))
        elif isinstance(error, commands.NotOwner):
            await ctx.send(embed = discord.Embed(description = f"You need to be the owner of the bot to do that.", color = discord.Color.red()))
        else:
            await ctx.send(embed = discord.Embed(description = f"Something went wrong: {error}", color = discord.Color.red()))


def setup(client):
    client.add_cog(_ErrorHandler(client))