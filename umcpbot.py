import discord
import asyncio
import time
import datetime
import json

servername = "UMCP Gaming"
# servername = "chilledtoadtestserver"
client = discord.Client()
#test server variables
rolerequest = ""
roles = []
aliases = {}
stats = {"channels":{},"members":{},"newmembers":0,"messages":0}
first_run = False


# Stats

def next_time():
    today = datetime.datetime.today()
    tomorrow = today.replace(hour=8, minute=0, second=0, microsecond=0)
    if (tomorrow < today):
        tomorrow = tomorrow + datetime.timedelta(days=1)

    print(tomorrow)
    return (tomorrow - today)


async def update_stats():
    global stats
    await client.wait_until_ready()
    server = discord.utils.find(lambda s: s.name == servername, client.servers)
    channel = discord.utils.find(lambda c: c.name == "stats", server.channels)
    while not client.is_closed:
        if len(stats["channels"]) > 0 and len(stats["members"]) > 0:
            topchannel = max(stats["channels"].keys(), key=(lambda k: stats["channels"][k]))
            topmember = max(stats["members"].keys(), key=(lambda k: stats["members"][k]))
            embed_message = "__**Most Active Member:**__\t\t" + topmember.display_name + " with " + str(stats["members"][topmember])
            embed_message+= " messages sent!\n__**Most Active Channel:**__\t\t" + topchannel.name + " with "
            embed_message+= str(stats["channels"][topchannel]) + " messages sent!\nThere were a total of " + str(stats["messages"])
            embed_message+= " messages sent today!\n\n" + str(stats["newmembers"]) + " new members joined today! Welcome!\n__**Total Members:**__\t" + str(len(server.members))

            em = discord.Embed(title='Today\'s Stats', description=embed_message, colour=0xFF0000)
            em.set_author(name='UMCP Gaming', icon_url=client.user.avatar_url)
            await client.send_message(channel, embed=em)
        # reset stats
        stats = {"channels":{},"members":{},"newmembers":0,"messages":0}
        today = datetime.datetime.today()
        next = next_time()
        await asyncio.sleep(next.total_seconds())

@client.event
async def on_message(message):
    global stats

    if message.author.bot:
        return

    # update stats
    stats["messages"] += 1
    if message.author in stats["members"]:
        stats["members"][message.author] += 1
    else:
        stats["members"][message.author] = 1

    if message.channel in stats["channels"]:
        stats["channels"][message.channel] += 1
    else:
        stats["channels"][message.channel] = 1

    # handle message
    parsed = message.content.split()
    user_roles = message.author.roles

    if(message.content.startswith('!addgame')):
        parsed = [x.lower() for x in list(set(parsed[1:]))]
        if(message.channel.id != rolerequest):
            await client.send_message(message.channel, 'Keep all role requests in the <#' + rolerequest + '> channel!')
            return

        for i in range(len(parsed)):
            for role in roles:
                add_role = ""
                if(role.name.lower() == parsed[i]):
                    add_role = parsed[i]
                keys = [key for key, value in aliases.items() if parsed[i] in
                        value]
                if keys:
                    add_role = keys[0] if keys[0] == role.name.lower() else add_role

                if add_role:
                    await client.send_message(message.channel, 'Adding ' + message.author.name + ' to ' + add_role + '...')
                    await client.add_roles(message.author, role)

    elif(message.content.startswith('!removegame')):
        parsed = [x.lower() for x in list(set(parsed[1:]))]
        if(message.channel.id != rolerequest):
            await client.send_message(message.channel, 'Keep all role requests in the <#' + rolerequest + '> channel!')
            return

        for role in roles:
            if role not in user_roles:
                continue
            for i in range(len(parsed)):
                add_role = ""
                if(role.name.lower() == parsed[i]):
                    add_role = parsed[i]
                keys = [key for key, value in aliases.items() if parsed[i] in
                        value]
                if keys:
                    add_role = keys[0] if keys[0] == role.name.lower() else add_role

                if add_role:
                    await client.send_message(message.channel, 'Removing ' + message.author.name + ' from ' + add_role + '...')
                    await client.remove_roles(message.author, role)


    elif(message.content.startswith('!help') or message.content.startswith('!list')):
        s = """ ```Markdown\n!help/!list - Displays this message\n"""
        s = s + """!addgame [game] <game> <game> ... - Add the game role(s) to allow access to the chat channels\n"""
        s = s + """!removegame [game] <game> <game> ... - Remove the game role(s)\n\nWe support """
        for role in roles[:-1]:
            s = s + role.name + ", "
        s = s + "and " + roles[-1].name
        s = s + """\n```"""
        await client.send_message(message.channel, s)

@client.event
async def on_member_join(member):
    stats["newmembers"] += 1
    s = "Welcome to UMCP Gaming, " + member.mention + "!\nLooks like you haven't added any games yet! It must seem pretty empty here.\n"
    s = s + "Head over to <#349781614877999104> and add your first game. "
    s = s + "After you do that, <#358005392648962059> will disappear and you will be able to engage with the communities that you choose to be in!\n"
    s = s + "Happy gaming!"
    await client.send_message(member, s)

### Automatically update roles

@client.event
async def on_server_role_create(role):
    updateRoles(server)

@client.event
async def on_server_role_delete(role):
    updateRoles(server)

@client.event
async def on_server_role_update(before, after):
    updateRoles(server)


def updateRoles(s):
    global roles
    roles = s.role_hierarchy
    i = 0
    for role in roles:
        if role.name == "Bot":
            roles = roles[i+1:-1]
            roles = [r for r in roles if not ' ' in r.name]
            break
        i += 1

@client.event
async def on_member_update(before, after):
    if(before.game):
        if((not after.game or after.game.type != 1) and before.game.type == 1):
            await client.remove_roles(after, discord.utils.find(lambda r: r.name == "Now Streaming", server.roles))
    if(after.game):
        if((not before.game or before.game.type != 1) and after.game.type == 1):
            await client.add_roles(after, discord.utils.find(lambda r: r.name == "Now Streaming", server.roles))

@client.event
async def on_ready():
    global roles, server, rolerequest, aliases
    server = discord.utils.find(lambda s: s.name == servername, client.servers)
    updateRoles(server)
    rolerequest = discord.utils.find(lambda c: c.name == "role-request", server.channels).id
    with open('aliases.json') as data_file:
        aliases = json.load(data_file)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

#start stats loop
client.loop.create_task(update_stats())

client.run('MzQ5NTk5MzA3MjAyMDM1NzE0.DH36AA.OpWuFqLsT35zjaeawqiv5bUJFzY') ### UMCP Gaming Bot
# client.run('MzUyNTAzNDI5ODkwOTY1NTE0.DKBn5Q.uzxPgF-95GSZyXvzYKrAIDoi0c8') ### ChilledToad
