import discord
import asyncio
import time
import json

servername = "chilledtoadtestserver"
client = discord.Client()
#test server variables
rolerequest = ""
roles = []
renamed_channels = {}
aliases = {}

@client.event
async def on_message(message):
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


    elif(message.content.startswith('!help')):
        s = """ ```Markdown\n!help - Displays this message\n"""
        s = s + """!addgame [game] <game> <game> ... - Add the game role(s) to allow access to the chat channels\n"""
        s = s + """!removegame [game] <game> <game> ... - Remove the game role(s)\n\nWe support """
        for role in roles[:-1]:
            s = s + role.name + ", "
        s = s + "and " + roles[-1].name
        s = s + """\n```"""
        await client.send_message(message.channel, s)

@client.event
async def on_member_join(member):
    s = "Welcome to UMCP Gaming, " + member.mention + "!\nLooks like you haven't added any games yet! It must seem pretty empty here.\n"
    s = s + "Head over to <#349781614877999104> and add your first game. "
    s = s + "After you do that, <#358005392648962059> will disappear and you will be able to engage with the communities that you choose to be in!\n"
    s = s + "Happy gaming!"
    await client.send_message(member, s)



@client.event
async def on_ready():
    global roles, server, rolerequest, aliases
    server = discord.utils.find(lambda s: s.name == servername, client.servers)
    updateRoles(server)
    rolerequest = discord.utils.find(lambda c: c.name == "role-request", server.channels).id
    with open('aliases.json') as data_file:
        aliases = json.load(data_file)
    print(aliases)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

### Automatic voice channel names

async def update_gamelobby_name(channel, members):
    member_games = {}
    for member in members:
        if member.game is not None:
            if member.game in member_games:
               member_games[member.game] = member_games[member.game] + 1
            else:
                member_games[member.game] = 1
    max_game = max(member_games, key=lambda k: member_games[k])
    await client.edit_channel(channel, name=max_game.name)

@client.event
async def on_voice_state_update(before, after):
    if(after.voice.voice_channel is not None):
        members = after.voice.voice_channel.voice_members
        id = after.voice.voice_channel.id
        if "Game Lobby" in after.voice_channel.name or id in renamed_channels:
            if id not in renamed_channels:
                renamed_channels[id] = after.voice.voice_channel.name

            await update_gamelobby_name(after.voice.voice_channel, members)

    if(before.voice.voice_channel is not None):
        members = before.voice.voice_channel.voice_members
        id = before.voice.voice_channel.id
        if id in renamed_channels:
            if len(members) == 0:
                await client.edit_channel(before.voice.voice_channel, name=renamed_channels[id])
                print(renamed_channels)
                renamed_channels.pop(id)
                print(renamed_channels)
            else:
                await update_gamelobby_name(before.voice.voice_channel, members)


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


### client.run('MzQ5NTk5MzA3MjAyMDM1NzE0.DH36AA.OpWuFqLsT35zjaeawqiv5bUJFzY') ### UMCP Gaming Bot
client.run('MzUyNTAzNDI5ODkwOTY1NTE0.DKBn5Q.uzxPgF-95GSZyXvzYKrAIDoi0c8') ### ChilledToad
