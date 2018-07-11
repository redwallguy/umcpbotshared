import discord
from discord.ext import commands
import os
import datetime
import redis

bot = commands.Bot()
token = os.environ.get("discToken")
r = redis.from_url(os.environ.get("REDIS_URL"))

@bot.event
async def on_ready():
    yesterday = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=-1)
    for serv in bot.guilds:
        if len(serv.text_channels) > 0:
            topchan = serv.text_channels[0]
            topchannum = len(await topchan.history(limit=1000,after=yesterday).flatten())
            for tc in serv.text_channels:
                tcnum = len(await tc.history(limit=1000, after=yesterday).flatten())
                if tcnum > topchannum:
                    topchan = tc
                    topchannum = tcnum

            topmemb = serv.members[0]
            topmembnum = 0
            allmsgs = []
            for tc in serv.text_channels:
                allmsgs.append(await tc.history(limit=1000,after=yesterday).flatten())
            for mem in serv.members:
                memnum = 0
                for msg in allmsgs:
                    if msg.author.id == mem.id:
                        memnum += 1
                if memnum > topmembnum:
                    topmemb = mem
                    topmembnum = memnum
            embedmsg = "__**Most Active Member**__\t\t" + topmemb.display_name
            embedmsg += " with " + str(topmembnum) + " messages sent!\n"
            embedmsg = "__**Most Active Channel**__\t\t" + topchan.name
            embedmsg += " with " + str(topchannum) + " messages sent!\n"
            embedmsg += str(r.get("newmem")) + " new members joined today! Welcome.\n"
            embedmsg += "**Total members**:\t " + str(len(serv.members))

            r.set("newmem"+serv.id,0)
            em = discord.Embed(title='Today\'s Stats', description=embedmsg, colour=0xFF0000)
            em.set_author(name='UMCP Gaming', icon_url=bot.user.avatar_url)
            statchan = discord.utils.get(serv.text_channels,name="stats")
            if statchan is not None:
                await statchan.send(embed=em)
    await bot.close()

bot.run(token)


