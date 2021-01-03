import discord
import datetime
import mysql.connector
import aiohttp
import json
import asyncio
from discord.ext import commands, tasks
from steam.steamid import SteamID
from discord.utils import get
from colorama import init, Fore
from discord.utils import get

init()

with open(f"./json/database.json", 'r') as file: # Get Bot Token
        db = json.load(file)['playersactivity']



# Database Connection
mydb = mysql.connector.connect(
    host=db['host'],
    user=db['user'],
    password=db['password'],
    database=db['database'])


cursor = mydb.cursor()

giveaway_ban_role_name = 'Giveaway Ban'
giveaway_role_name = 'Giveaway Member'
vip_role_name = 'VIP'
minumum_activity = 36000

def set_all_discord_ids():
    cursor.execute("SELECT * from players_activity WHERE discord_id !='None'")
    database_list = cursor.fetchall()
    jump_over = []
    for row in database_list:
        if row[0] not in jump_over:
            cursor.execute(
                "UPDATE players_activity SET discord_id = '%s' WHERE steamid = '%s'" % (row[3], row[0]))
            jump_over.append(row[0])
    mydb.commit()

def is_banned(author_roles):
    for role in author_roles:
        if role.name == giveaway_ban_role_name:
            return True
    return False

def get_steamid3(url):
    steamid64 = int(SteamID.from_url(url))
    group = SteamID(steamid64)
    return group.as_steam3

def extract_id_from_steamid3(steamid3):
    return int(steamid3[5:-1])

class Activity(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.checkDB.start()
        self.giveroles.start()
        self.set_discord_id.start()
    
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{Fore.RED}Activity cog Ready!')



    @commands.command(aliases=['app'], description='Apply for activity', help='apply [steamurl]')
    async def apply(self, ctx, steamurl):

        embed = discord.Embed(author = ctx.author.name)

        try:
            steamid3 = extract_id_from_steamid3(get_steamid3(steamurl))
        except:
            embed.description = f"{ctx.author.name}. That's not a valid steam profile link.\nYour steam profile link must look something like `https://steamcommunity.com/id/NAME/`"
            embed.color = discord.Color.green()
        else:
            if not mydb.is_connected():
                mydb.connect()

            cursor.execute("SELECT steamid, discord_id FROM players_activity WHERE steamid = '%s'" % steamid3)

            discord_id_list = cursor.fetchall()
            if discord_id_list:
                if discord_id_list[0][1] is None:
                    cursor.execute("UPDATE players_activity SET discord_id = '%s' WHERE steamid = '%s'" % (ctx.author.id, steamid3))
                    embed.description =f"Your Discord ID has been added to database.\nIf your activity is over **{round(float(minumum_activity / 3600), 2)}** hours, you will get your Giveaway Member role soon."
                    embed.color = discord.Color.green()
                else:
                    embed.description = f"Sorry but that Steam Profile is already associated with an Discord ID (<@{discord_id_list[0][1]}>). Contact a Manager for more information"
                    embed.color = discord.Color.red()
            else:
                embed.description = "Sorry but I can't find your SteamID in the database."
                embed.color = discord.Color.red()
            mydb.commit()

        await ctx.send(embed=embed)


    @commands.command(alises=['prof'], description='Check server profile', help='profile (users)')
    async def profile(self, ctx, user: discord.Member = ''):
        if user == '':
            member = ctx.author
        else:
            member = user

        if not mydb.is_connected():
                mydb.connect()

        embed = discord.Embed(color=discord.Color.orange())
        cursor.execute("SELECT * FROM players_activity WHERE discord_id = '%s'" % member.id)
        activity_list= cursor.fetchall()
        if activity_list:
            group = SteamID(activity_list[0][0])
            session = aiohttp.ClientSession()
            response = await session.get(f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=892E7FF7A834087D6E16F9F073D73F67&steamids={group.as_64}')
            data = json.loads(await response.text())
            await session.close()
            steam_name = data['response']['players'][0]['personaname']
            steam_profile_pic = data['response']['players'][0]['avatarfull']
            steam_id_2 = group.as_steam2
            steam_profile_url = group.community_url
            month_activity = sum([day[2] for day in activity_list])
            date_list = [day[1] for day in activity_list]
            embed.set_author(name=f"{member.name}'s profile.")
            embed.description = f"**[Steam Profile]({steam_profile_url})**"
            embed.add_field(name=':label:SteamID', value=f'**`{steam_id_2}`**', inline=False)
            embed.add_field(name=':bust_in_silhouette:Steam Name', value = f'**{steam_name}**', inline=False)
            embed.add_field(name=':clock4:Last activity', value=f'**{max(date_list)}**', inline=True)
            embed.add_field(name=':hourglass_flowing_sand:Activity past month', value=f'**{round(month_activity / 3600, 2)} hours.**', inline=True)
            embed.add_field(name=':warning:Giveaway Ban', value=f'**{":x:Yes" if is_banned(member.roles) else ":white_check_mark:No"}**', inline=True)
            embed.set_thumbnail(url=steam_profile_pic)
        else:
            if user == None:
                embed.description = f"{ctx.author.name}. I could not find your profile. Maybe you haven't joined our servers in more than a month\nOr you haven't applied yet. Type `{ctx.command.prefix} apply [steamurl]`"
            else:
                embed.description = f"{ctx.author.name}. I could not find this user profile. Maybe he hasn't joined our servers in more than a month\n"
            embed.color = discord.Color.red()

        await ctx.send(embed=embed)

    @commands.command(aliases=['t'], description='Show top activity', help='top (amount)')
    async def top(self, ctx, amount=3):
        if amount > 10:
            amount = 10

        if not mydb.is_connected():
                    mydb.connect()
        embed = discord.Embed(color=discord.Color.orange())
        activity_dic = {}
        cursor.execute("SELECT discord_id, seconds  FROM players_activity WHERE discord_id != 'None'")
        players_activity = cursor.fetchall()
        for player in players_activity:
            if player[0] not in activity_dic:
                activity_dic[player[0]] = player[1]
            else:
                activity_dic[player[0]] += player[1]
        activity_dic = sorted(activity_dic.items(), key=lambda x: x[1], reverse=True)

        if amount > len(activity_dic):
            amount = len(activity_dic)

        member = self.client.get_user(468179605124153344)
        embed.set_author(name=f"Top {amount}.")
        for i in range(amount):
            try:
                if i == 0:
                    member = self.client.get_user(int(activity_dic[i][0]))
                    activity = f"{round(activity_dic[i][1] / 3600, 2)} hours"

                    embed.add_field(name=f":first_place:Top {i+1}", value=f"{member.name} -- `{activity}`", inline=False)
                elif i == 1:
                    member = self.client.get_user(int(activity_dic[i][0]))
                    activity = f"{round(activity_dic[i][1] / 3600, 2)} hours"
                    embed.add_field(name=f":second_place:Top {i+1}", value=f"{member.name} -- `{activity}`", inline=False)
                elif i == 2:
                    member = self.client.get_user(int(activity_dic[i][0]))
                    activity = f"{round(activity_dic[i][1] / 3600, 2)} hours"
                    embed.add_field(name=f":third_place:Top {i+1}", value=f"{member.name} -- `{activity}`", inline=False)
                else:
                    member = self.client.get_user(int(activity_dic[i][0]))
                    activity = f"{round(activity_dic[i][1] / 3600, 2)} hours"
                    embed.add_field(name=f"Top {i+1}", value=f"{member.name} -- `{activity}`", inline=False)
            except Exception as e:
                print(e)

        await ctx.send(embed=embed)

    @tasks.loop(seconds=86400)
    async def checkDB(self):
        if not mydb.is_connected():
                    mydb.connect()
        print("Clean Db....")
        set_all_discord_ids()
        cursor.execute("SELECT steamid, date FROM players_activity")
        database_list = cursor.fetchall()
        date_now = datetime.date.today()
        for date in database_list:
            delta = date_now - date[1]
            days = delta.days

            if days > 31:
                try:
                    await asyncio.sleep(0.01)
                    cursor.execute("DELETE FROM players_activity WHERE steamid = '%s' and date = '%s'" % (date[0], date[1]))
                except Exception as e:
                    print(e)

        print("Database Cleaned!")
        mydb.commit()
    
    @tasks.loop(seconds = 1800)
    async def set_discord_id(self):
        if not mydb.is_connected():
                    mydb.connect()
        set_all_discord_ids()
    
    @tasks.loop(seconds=5)
    async def giveroles(self):
        if not mydb.is_connected():
                    mydb.connect()
        activity_dic = {}

        cursor.execute("SELECT discord_id, seconds  FROM players_activity WHERE discord_id != 'None'")
        players_activity = cursor.fetchall()

        for player in players_activity:
            if player[0] not in activity_dic:
                activity_dic[player[0]] = player[1]
            else:
                activity_dic[player[0]] += player[1]

        activity_dic = sorted(activity_dic.items(), key=lambda x: x[1], reverse=True)

        for user in activity_dic:
            if user[1] < minumum_activity:
                for guild in self.client.guilds:
                    try:
                        member = guild.get_member(int(user[0]))
                        role_remove = discord.utils.get(guild.roles, name=giveaway_role_name).id
                        banned = False
                        if role_remove != None and member != None:
                            for role in member.roles:
                                if role.name == giveaway_ban_role_name:
                                    banned = True
                            if banned == False:
                                await member.remove_roles(guild.get_role(role_remove))

                    except Exception as e:
                        print(e)

            else:
                for guild in self.client.guilds:
                    try:
                        member = guild.get_member(int(user[0]))
                        role_add = discord.utils.get(guild.roles, name=giveaway_role_name).id
                        banned = False
                        for role in member.roles:
                            if role.name == giveaway_ban_role_name:
                                banned = True
                        if banned == False:
                            await member.add_roles(guild.get_role(role_add))
                    except Exception as e:
                        print(e)

        mydb.commit()


def setup(client):
    client.add_cog(Activity(client))
