import discord
import os
from discord.ext import commands
import redis
import psycopg2
import datetime
import celery
import requests
import json

bot = commands.Bot(command_prefix="!")
token = os.environ.get("DISC_TOKEN")
r = redis.from_url(os.environ.get("REDIS_URL"))

dburl = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(dburl, sslmode="require")
cur = conn.cursor()

app = celery.Celery('umcpbot', broker=os.environ.get("REDIS_URL"))

@app.task
def remind(aid, message):
    remindObj.rem_user(aid)
    requests.post(os.environ.get("WEBHOOK_URL"),headers={'Content-Type': 'application/json'}, json={'content': message})

class Remind:
    def __init__(self):
        with open("reminder.json", "w") as f:
            json.dump({},f)

    def is_pending(self, aid):
        with open("reminder.json") as f:
            if str(aid) in json.load(f):
                return True
            else:
                return False

    def add_user(self, aid):
        with open("reminder.json", "r") as f:
            rd = json.load(f)
            rd[aid] = "0"
        with open("reminder.json", "w") as f:
            json.dump(rd, f)

    def rem_user(self, aid):
        with open("reminder.json", "r") as f:
            rd = json.load(f)
            rd.pop(str(aid), "1")
        with open("reminder.json", "w") as f:
            json.dump(rd, f)

class Games:
    def __init__(self):
        cur.execute("SELECT * FROM games;")
        glist = cur.fetchall()
        self.games = {}
        for g in glist:
            self.games[g[0]] = []
        for key in self.games:
            cur.execute("SELECT (alias) FROM aliases WHERE game = %s", (key,))
            alilist = cur.fetchall()
            for ali in alilist:
                self.games[key].append(ali[0])

    def get_games(self):
        return self.games

    def add_game(self, game):
        try:
            cur.execute("INSERT INTO (games) VALUES (%s)", (game,))
            self.games[game] = []
        except:
            return "Game already exists."

    def add_alias(self, alias, game):
        try:
            cur.execute("INSERT INTO aliases (alias, game) VALUES (%s,%s)", (alias, game))
            self.games[game].append(alias)
        except:
            return "Oops! Something went wrong."

    def remove_alias(self, alias, game):
        try:
            cur.execute("DELETE FROM aliases WHERE alias = %s", (alias,))
            self.games[game].remove(alias)
        except:
            return

    def remove_game(self, game):
        try:
            cur.execute("DELETE FROM games WHERE game = %s", (game,))
            self.games.pop(game, None)
        except:
            return

gameObj = Games()
remindObj = Remind()


@bot.command()
async def addgame(ctx, *games):
    """
    Adds game(s) to your roles.

    Usage: !addgame game1 game2 ...
    Maximum 10 games added at once
    """
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
                    await ctx.author.add_roles(role_to_add)


@bot.command()
async def removegame(ctx, *games):
    """
    Removes game(s) from your roles.

    Usage: !removegame game1 game2 ...
    Maximum 10 games removed at once
    """
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
                    await ctx.author.remove_roles(role_to_rem)


@bot.command()
async def addall(ctx):
    """
    Adds all games to your roles.
    UNLIMITED POWAHHHH
    """
    for game in gameObj.get_games():
        role_to_add = discord.utils.get(ctx.guild.roles, name=game)
        if role_to_add is not None:
            await ctx.author.add_roles(role_to_add)


@bot.command()
async def removeall(ctx):
    """
    Removes all games from your roles.
    Et ego dabo vobis tabula rasa...
    """
    for game in gameObj.get_games():
        role_to_rem = discord.utils.get(ctx.guild.roles, name=game)
        if role_to_rem is not None:
            await ctx.author.add_roles(role_to_rem)

async def no_reminder(ctx):
    if remindObj.is_pending(ctx.author.id):
        return False
    else:
        return True

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
@commands.check(no_reminder)
async def remindafter(ctx, hours: int, minutes: int, msg=None):
    """
    Sends reminder back to the channel after [hours] hours and [minutes] minutes, with the given message.

    If no message is provided, then the message '[author] has been reminded!' will be sent by default.
    The furthest in the future you can set a reminder is 2 weeks.
    Each user may only have one reminder pending, with maximum 30 total reminders over the entire server.
    """
    default_msg = "<@" + str(ctx.author.id) + ">" + " has been reminded!"
    delay_in_sec = (hours*3600) + (minutes*60)
    if hours < 0 or minutes < 0:
        await ctx.send("I can't go back in time, sorry.")
        return
    if delay_in_sec > 1209600:
        await ctx.send("You can only set a reminder up to 2 weeks in advance.")
        return
    if msg is None:
        remind.apply_async(args=[ctx.author.id, default_msg], countdown=delay_in_sec)
        remindObj.add_user(ctx.author.id)
        return
    else:
        remind.apply_async(args=[ctx.author.id, "<@" + str(ctx.author.id) + ">" + msg], countdown=delay_in_sec)
        remindObj.add_user(ctx.author.id)
        return

def to_date(dt):
    dt_split = dt.split("/")
    if len(dt_split) != 4:
        print("Err 1")
        raise commands.BadArgument()
    else:
        try:
            month = int(dt_split[0])
            day = int(dt_split[1])
            year = int(dt_split[2])
        except ValueError:
            print("Err 2")
            raise commands.BadArgument()
        else:
            time_given = dt_split[3]
            time_split = time_given.split(":")
            if len(time_split) != 2:
                print("Err 3")
                raise commands.BadArgument()
            else:
                try:
                    hour = int(time_split[0])
                    minute = int(time_split[1])
                except ValueError:
                    print("Err 4")
                    raise commands.BadArgument()
                else:
                    try:
                        date = datetime.datetime(year=year,month=month,day=day,hour=hour,minute=minute,
                                                 tzinfo=datetime.timezone.utc)
                    except ValueError:
                        print("Err 5")
                        raise commands.BadArgument()
                    else:
                        if datetime.datetime.now(datetime.timezone.utc) - date > datetime.timedelta(seconds=0) or date - datetime.datetime.now(datetime.timezone.utc) > datetime.timedelta(weeks=2):
                            print("Err 6")
                            raise commands.BadArgument()
                        else:
                            return date


@bot.command()
@commands.check(no_reminder)
async def remindat(ctx, date: to_date, msg=None):
    """
    Sends reminder back to channel at time specified by [date] with the given message.
    Date should be formatted as mm/dd/yyyy/hh:mm (UTC time).

    If no message is provided, then the message '[author] has been reminded!' will be sent by default.
    The furthest in the future you can set a reminder is 2 weeks.
    Each user may only have one reminder pending, with maximum 30 total reminders over the entire server.
    """
    default_msg = "<@" + str(ctx.author.id) + ">" + " has been reminded!"
    if msg is None:
        remind.apply_async(args=[ctx.author.id, default_msg], eta=date)
        remindObj.add_user(ctx.author.id)
        return
    else:
        remind.apply_async(args=[ctx.author.id, "<@"+str(ctx.author.id)+">"+ msg], eta=date)
        remindObj.add_user(ctx.author.id)

@remindat.error
async def remindat_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Your reminder time is bad. Type !help remindat to see the rules for setting a reminder.")

if __name__ == '__main__':
    bot.run(token)
#TODO admin add/remove games from db (@bot.check(isAdmin))
#TODO celery support for remindme feature