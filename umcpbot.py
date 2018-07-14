import discord
import asyncio
import os
from discord.ext import commands
import redis
import psycopg2

bot = commands.Bot(command_prefix="!")
token = os.environ.get("discToken")
r = redis.from_url(os.environ.get("REDIS_URL"))

dburl = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(dburl, sslmode="require")
cur = conn.cursor()


class Games:
    def __init__(self):
        cur.execute("SELECT * FROM games;")
        glist = cur.fetchall()
        self.games = {}
        for g in glist:
            self.games[g[0]] = []
        for key in self.games:
            cur.execute("SELECT (alias) FROM aliases WHERE game = %s", key)
            alilist = cur.fetchall()
            for ali in alilist:
                self.games[key].append(ali[0])

    def get_games(self):
        return self.games

    def add_game(self, game):
        try:
            cur.execute("INSERT INTO (games) VALUES (%s)", game)
            self.games[game] = []
        except:
            return "Game already exists."

    def add_alias(self, alias, game):
        try:
            cur.execute("INSERT INTO aliases (alias, game) VALUES (%s,%s)", alias, game)
            self.games[game].append(alias)
        except:
            return "Oops! Something went wrong."

    def remove_alias(self, alias, game):
        try:
            cur.execute("DELETE FROM aliases WHERE alias = %s", alias)
            self.games[game].remove(alias)
        except:
            return

    def remove_game(self, game):
        try:
            cur.execute("DELETE FROM games WHERE game = %s", game)
            self.games.pop(game, None)
        except:
            return

gameObj = Games()

@bot.event
async def on_member_join(member):
    r.incr("newmem"+member.guild.id)
    readmechan = discord.utils.get(member.guild.text_channels, name="important-readme")
    rolereqchan = discord.utils.get(member.guild.text_channels, name="role-request")
    msg = "Welcome to UMCP Gaming, " + member.mention + "! "
    msg += "To get started, head over to " + rolereqchan.mention + " and add a game"
    msg += " using the !addgame command. Once you do so, you can view and interact with that game's"
    msg += " voice and text channels, and " + readmechan.mention + " will disappear."
    await member.send(msg)

@bot.command()
async def addgame(ctx, *games):
    if len(games) == 0:
        await ctx.send("No game provided.")
        return
    elif len(games) > 10:
        numgames = 10
    else:
        numgames = len(games)
    for i in range(numgames):
        for game in gameObj.get_games():
            if games[i].lower() == game.lower() or games[i].lower() in gameObj.get_games()[game]:
                role_to_add = discord.utils.get(ctx.guild.roles, name=game)
                if role_to_add is not None:
                    ctx.author.add_roles(role_to_add)

@bot.command()
async def removegame(ctx, *games):
    if len(games) == 0:
        await ctx.send("No game provided.")
        return
    elif len(games) > 10:
        numgames = 10
    else:
        numgames = len(games)
    for i in range(numgames):
        for game in gameObj.get_games():
            if games[i].lower() == game.lower() or games[i].lower() in gameObj.get_games()[game]:
                role_to_rem = discord.utils.get(ctx.guild.roles, name=game)
                if role_to_rem is not None:
                    ctx.author.remove_roles(role_to_rem)

@bot.command()
async def addall(ctx):
    for game in gameObj.get_games():
        role_to_add = discord.utils.get(ctx.guild.roles, name=game)
        if role_to_add is not None:
            ctx.author.add_roles(role_to_add)

@bot.command()
async def removeall(ctx):
    for game in gameObj.get_games():
        role_to_rem = discord.utils.get(ctx.guild.roles, name=game)
        if role_to_rem is not None:
            ctx.author.add_roles(role_to_rem)

#TODO admin add/remove games from db (@bot.check(isAdmin))
#TODO celery support for remindme feature