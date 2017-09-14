import discord
import asyncio
import time

client = discord.Client()
#test server variables
server = '349777729861976064'
rolerequest = '349777729861976065'
firsthelp = '349933666287484929'
#release server variables
server = '348919724635324419'
rolerequest = '349781614877999104'
firsthelp = '357979853770981377'
roles = []


help_message = """ ```Markdown
!help - Displays this message
!addgame [game] <game> <game> ... - Add the game role(s) to allow access to the chat channels
!removegame [game] <game> <game> ... - Remove the game role(s)

We support overwatch, league, smash, rocketleague, heroes, starcraft, hearthstone, csgo, pubg, and destiny
```

        """

@client.event
async def on_message(message):
    global help_message
    parsed = message.content.split()
    user_roles = message.author.roles

    if(message.content.startswith('!addgame')):
        parsed = [x.lower() for x in list(set(parsed[1:]))]
        if(message.channel.id != rolerequest):
            await client.send_message(message.channel, 'Keep all role requests in the <#' + rolerequest + '> channel!')
            return

        incorrect_syntax = False
        not_found = True

        for role in roles:
            if role in user_roles:
                continue
            for i in range(len(parsed)):
                if parsed[i] == "hots":
                    not_found = False
                    parsed[i] = "heroes"
                if(role.name == parsed[i] and role.name != 'Admin' and role.name != 'Bot'):
                    not_found = False
                    await client.send_message(message.channel, 'Adding ' + message.author.name + ' to ' + parsed[i] + '...')
                    await client.add_roles(message.author, role)

            if not not_found:
                incorrect_syntax = True

        if(incorrect_syntax):
            await client.send_message(message.channel, help_message)

    elif(message.content.startswith('!removegame')):
        parsed = [x.lower() for x in list(set(parsed[1:]))]
        if(message.channel.id != rolerequest):
            await client.send_message(message.channel, 'Keep all role requests in the <#' + rolerequest + '> channel!')
            return

        for role in roles:
            if role not in user_roles:
                continue
            for i in range(len(parsed)):
                if(role.name == parsed[i] and role.name != 'Admin' and role.name != 'Bot'):
                    await client.send_message(message.channel, 'Removing ' + message.author.name + ' from ' + parsed[i] + '...')
                    await client.remove_roles(message.author, role)


    elif(message.content.startswith('!')):
        await client.send_message(message.channel, help_message)


@client.event
async def on_ready():
    global roles, server, firsthelp
    server = client.get_server(server)
    roles = server.roles
    firsthelp = client.get_message(server.get_channel(rolerequest), firsthelp)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run('MzQ5NTk5MzA3MjAyMDM1NzE0.DH36AA.OpWuFqLsT35zjaeawqiv5bUJFzY')
