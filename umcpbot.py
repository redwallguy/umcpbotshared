import discord
import os
from discord.ext import commands
import redis
import psycopg2
import datetime
import celery
import requests
import json
import time

bot = commands.Bot(command_prefix="!")
token = os.environ.get("DISC_TOKEN")
r = redis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)

dburl = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(dburl, sslmode="require")
cur = conn.cursor()

app = celery.Celery('umcpbot', broker=os.environ.get("REDIS_URL"))


@app.task
def remind(aid, message):
    remindObj.dec_user(aid)
    requests.post(os.environ.get("WEBHOOK_URL"), headers={'Content-Type': 'application/json'},
                  json={'content': message})


class Remind:

    def __init__(self):
        self.REMINDER_LIMIT = 5
        if r.get("reminder") is None:
            r.set("reminder", json.dumps({}))
            self.remind_dict = {}
        else:
            self.remind_dict = json.loads(r.get("reminder"))

    def num_pending(self, aid):
        aid = str(aid)
        if aid in self.remind_dict:
            return self.remind_dict[aid]
        else:
            return 0

    def inc_user(self, aid):
        aid = str(aid)
        if self.num_pending(aid) == 0:
            self.remind_dict[aid] = 1
        else:
            self.remind_dict[aid] += 1
        r.set("reminder", json.dumps(self.remind_dict))

    def dec_user(self, aid):
        aid = str(aid)
        if self.num_pending(aid) <= 0:
            self.remind_dict[aid] = 0
        else:
            self.remind_dict[aid] -= 1
        r.set("reminder", json.dumps(self.remind_dict))


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
        except Exception as e:
            return e

    def add_alias(self, alias, game):
        try:
            cur.execute("INSERT INTO aliases (alias, game) VALUES (%s,%s)", (alias, game))
            self.games[game].append(alias)
        except Exception as e:
            return e

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


async def rolechan(ctx):
    if ctx.channel.name == "role-request":
        return True
    else:
        return False


@bot.command(aliases=["addgame"])
@commands.check(rolechan)
async def addrole(ctx, *games):
    """
    Adds roles) to your roles.

    Usage: !addrole game1 game2 ...
    Maximum 10 roles added at once.
    If a role/game is more than one word, wrap it in quotes; e.g, !addgame "rocket league"
    """
    if len(games) == 0:
        await ctx.send("No game provided.")
        return
    elif len(games) > 10:
        numgames = 10
    else:
        numgames = len(games)
    retmsg = "You have been added to\n-----------\n"
    for i in range(numgames):
        for game in gameObj.get_games():
            if games[i].lower() == game.lower() or games[i].lower() in gameObj.get_games()[game]:
                role_to_add = discord.utils.get(ctx.guild.roles, name=game)
                if role_to_add is not None:
                    await ctx.author.add_roles(role_to_add)
                    retmsg += game + "\n"
    if retmsg != "You have been added to\n-----------\n":
        await ctx.send(retmsg)


@bot.command(aliases=["removegame"])
@commands.check(rolechan)
async def removerole(ctx, *games):
    """
    Removes role(s) from your roles.

    Usage: !removerole game1 game2 ...
    Maximum 10 roles removed at once.
    If a role/game is more than one word, wrap it in quotes; e.g, !removegame "rocket league"
    """
    if len(games) == 0:
        await ctx.send("No game provided.")
        return
    elif len(games) > 10:
        numgames = 10
    else:
        numgames = len(games)
    retmsg = "You have been removed from\n-----------\n"
    for i in range(numgames):
        for game in gameObj.get_games():
            if games[i].lower() == game.lower() or games[i].lower() in gameObj.get_games()[game]:
                role_to_rem = discord.utils.get(ctx.guild.roles, name=game)
                if role_to_rem is not None:
                    await ctx.author.remove_roles(role_to_rem)
                    retmsg += game + "\n"
    if retmsg != "You have been removed from\n-----------\n":
        await ctx.send(retmsg)


@bot.command()
@commands.check(rolechan)
async def addall(ctx):
    """
    Adds all roles to your roles.
    UNLIMITED POWAHHHH
    """
    for game in gameObj.get_games():
        role_to_add = discord.utils.get(ctx.guild.roles, name=game)
        if role_to_add is not None:
            await ctx.author.add_roles(role_to_add)
    await ctx.send("You have been added to all games. ")


@bot.command()
@commands.check(rolechan)
async def removeall(ctx):
    """
    Removes all roles from your roles.
    Et ego dabo vobis tabula rasa...
    """
    for game in gameObj.get_games():
        role_to_rem = discord.utils.get(ctx.guild.roles, name=game)
        if role_to_rem is not None:
            await ctx.author.remove_roles(role_to_rem)
    await ctx.send("You have been removed from all games.")


@bot.command()
@commands.check(rolechan)
async def roles(ctx):
    """
    Lists all roles/games supported, as well as their aliases.
    """
    gamemsg = "Roles/Games supported:\n--------------\n"
    for game in sorted(gameObj.get_games()):
        gamemsg += game + " ["
        for ali in gameObj.get_games()[game]:
            gamemsg += ali + ", "
        gamemsg += "]\n"
    await ctx.send(gamemsg)


@bot.command()
@commands.check(rolechan)
async def myroles(ctx):
    """
    Lists all roles/games you are added to.
    """
    gamemsg = "Your roles/games\n-----------\n"
    for game in gameObj.get_games():
        if discord.utils.get(ctx.author.roles, name=game) is not None:
            gamemsg += game + "\n"
    await ctx.send(gamemsg)


@bot.event
async def on_member_update(before, after):
    if before.activity is not None:
        if before.activity.type == discord.ActivityType.streaming:
            if after.activity is None and discord.utils.get(after.roles, name="Now Streaming") is not None:
                await after.remove_roles(discord.utils.get(after.roles, name="Now Streaming"))
                return
            elif after.activity.type != discord.ActivityType.streaming and discord.utils.get(after.roles,
                                                                                             name="Now Streaming") is not None:
                await after.remove_roles(discord.utils.get(after.roles, name="Now Streaming"))
                return
    elif after.activity is not None:
        if after.activity.type == discord.ActivityType.streaming:
            if before.activity is None and discord.utils.get(after.roles, name="Now Streaming") is None:
                await after.add_roles(discord.utils.get(after.roles, name="Now Streaming"))
                return
            elif before.activity.type != discord.ActivityType.streaming and discord.utils.get(after.roles,
                                                                                              name="Now Streaming") is None:
                await after.add_roles(discord.utils.get(after.roles, name="Now Streaming"))
                return


def reminder_lim(ctx):
    if remindObj.num_pending(ctx.author.id) <= remindObj.REMINDER_LIMIT:
        return True
    else:
        return False


@bot.event
async def on_member_join(member):
    readmechan = discord.utils.get(member.guild.text_channels, name="important-readme")
    rolereqchan = discord.utils.get(member.guild.text_channels, name="role-request")
    msg = "Welcome to UMCP Gaming, " + member.mention + "! "
    msg += "To get started, head over to " + rolereqchan.mention + " and add a game"
    msg += " using the !addgame command. Once you do so, you can view and interact with that game's"
    msg += " voice and text channels, and " + readmechan.mention + " will disappear."
    await member.send(msg)


@bot.command()
@commands.check(reminder_lim)
@commands.has_role("Officer")
async def remindafter(ctx, hours: int, minutes: int, msg=None):
    """
    Sends reminder back to the channel after [hours] hours and [minutes] minutes, with the given message.

    If no message is provided, then the message '[author] has been reminded!' will be sent by default.
    The furthest in the future you can set a reminder is 2 weeks.
    Each user may only have one reminder pending, with maximum 30 total reminders over the entire server.
    """
    default_msg = "<@" + str(ctx.author.id) + ">" + " has been reminded!"
    delay_in_sec = (hours * 3600) + (minutes * 60)
    if hours < 0 or minutes < 0:
        await ctx.send("I can't go back in time, sorry.")
        return
    if delay_in_sec > 1209600:
        await ctx.send("You can only set a reminder up to 2 weeks in advance.")
        return
    if msg is None:
        remind.apply_async(args=[ctx.author.id, default_msg], countdown=delay_in_sec)
        remindObj.inc_user(ctx.author.id)
        return
    else:
        remind.apply_async(args=[ctx.author.id, "<@" + str(ctx.author.id) + ">" + msg], countdown=delay_in_sec)
        remindObj.inc_user(ctx.author.id)
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
                        date = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute,
                                                 tzinfo=datetime.timezone.utc)
                    except ValueError:
                        print("Err 5")
                        raise commands.BadArgument()
                    else:
                        if datetime.datetime.now(datetime.timezone.utc) - date > datetime.timedelta(
                                seconds=0) or date - datetime.datetime.now(datetime.timezone.utc) > datetime.timedelta(
                                weeks=2):
                            print("Err 6")
                            raise commands.BadArgument()
                        else:
                            return date


@bot.command()
@commands.check(reminder_lim)
@commands.has_role("Officer")
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
        remindObj.inc_user(ctx.author.id)
        return
    else:
        remind.apply_async(args=[ctx.author.id, "<@" + str(ctx.author.id) + "> " + msg], eta=date)
        remindObj.inc_user(ctx.author.id)


@remindat.error
async def remindat_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Your reminder time is bad. Type !help remindat to see the rules for setting a reminder.")


if __name__ == '__main__':
    while True:
        try:
            bot.run(token)
        except Exception as e:
            print(e)
            time.sleep(60)