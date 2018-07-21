import discord
import os
from discord.ext import commands
import redis
import psycopg2
import celery
import datetime
import requests

bot = commands.Bot(command_prefix="!")
token = os.environ.get("discToken")
r = redis.from_url(os.environ.get("REDIS_URL"))

dburl = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(dburl, sslmode="require")
cur = conn.cursor()

app = celery.Celery('umcp_celery', broker=os.environ.get("REDIS_URL"))

@app.task
def remind(aid, message):
    r.lrem("reminderlist",aid)
    requests.post(os.environ.get("WEBHOOK_URL"),headers={'Content-Type': 'application/json'},
                      data={'content': message})

async def no_reminder(ctx):
    numrem = r.lrem("reminderlist", ctx.author.id)
    if numrem != 0:
        r.lpush("reminderlist", ctx.author.id)
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
    default_msg = ctx.author.name + " has been reminded!"
    delay_in_sec = (hours*3600) + (minutes*60)
    if hours < 0 or minutes < 0:
        await ctx.send("I can't go back in time, sorry.")
        return
    if delay_in_sec > 1209600:
        await ctx.send("You can only set a reminder up to 2 weeks in advance.")
        return
    if msg is None:
        remind.apply_async(args=[ctx.author.id, default_msg], countdown=delay_in_sec)
        r.lpush("reminderlist", ctx.author.id)
        return
    else:
        remind.apply_async(args=[ctx.author.id, msg], countdown=delay_in_sec)
        r.lpush("reminderlist", ctx.author.id)
        return

def to_date(dt):
    dt_split = dt.split("/")
    if len(dt_split) != 4:
        raise commands.BadArgument()
    else:
        try:
            month = int(dt_split[0])
            day = int(dt_split[1])
            year = int(dt_split[2])
        except ValueError:
            raise commands.BadArgument()
        else:
            time_given = dt_split[3]
            time_split = time_given.split(":")
            if len(time_split) != 2:
                raise commands.BadArgument()
            else:
                try:
                    hour = int(time_split[0])
                    minute = int(time_split[1])
                except ValueError:
                    raise commands.BadArgument()
                else:
                    try:
                        date = datetime.datetime(year=year,month=month,day=day,hour=hour,minute=minute,
                                                 tzinfo=datetime.timezone.utc)
                    except ValueError:
                        raise commands.BadArgument()
                    else:
                        if datetime.datetime.now(datetime.timezone.utc) - date > datetime.timedelta(seconds=0) or date - datetime.datetime.now(tzinfo=datetime.timezone.utc) > datetime.timedelta(weeks=2):
                            raise commands.BadArgument()
                        else:
                            return date


@bot.command()
@commands.check(no_reminder)
async def remindat(ctx, date: to_date, msg=None):
    """
    Sends reminder back to channel at time specified by [date] with the given message.
    Date should be formatted as mm/dd/yyyy/hh:mm.

    If no message is provided, then the message '[author] has been reminded!' will be sent by default.
    The furthest in the future you can set a reminder is 2 weeks.
    Each user may only have one reminder pending, with maximum 30 total reminders over the entire server.
    """
    default_msg = ctx.author.name + " has been reminded!"
    if msg is None:
        remind.apply_async(args=[ctx.author.id, default_msg], eta=date)
        r.lpush("reminderlist",ctx.author.id)
        return
    else:
        remind.apply_async(args=[ctx.author.id,  msg], eta=date)
        r.lpush("reminderlist", ctx.author.id)
        return

@remindat.error
async def remindat_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Your reminder time is bad. Type !help remindat to see the rules for setting a reminder.")

bot.run(token)
#TODO admin add/remove games from db (@bot.check(isAdmin))
#TODO celery support for remindme feature