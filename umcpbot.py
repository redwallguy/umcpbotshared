import discord
import asyncio

client = discord.Client()
#test server variables
server = '349777729861976064'
rolerequest = '349777729861976065'
#release server variables
server = '348919724635324419'
rolerequest = '348933488746954752'
roles = []

@client.event
async def on_message(message):
    parsed = message.content.split()
    user_roles = message.author.roles

    if(message.content.startswith('!addgame')):
        parsed = list(set(parsed[1:]))
        if(message.channel.id != rolerequest):
            await client.send_message(message.channel, 'Keep all role requests in the <#348933488746954752> channel!')
            return

        for role in roles:
            if role in user_roles:
                continue
            for i in range(len(parsed)):
                if(role.name == parsed[i] and role.name != 'Admin' and role.name != 'Bot'):
                    await client.send_message(message.channel, 'Adding ' + message.author.name + ' to ' + parsed[i] + '...')
                    await client.add_roles(message.author, role)

    if(message.content.startswith('!removegame')):
        parsed = list(set(parsed[1:]))
        if(message.channel.id != rolerequest):
            await client.send_message(message.channel, 'Keep all role requests in the <#348933488746954752> channel!')
            return

        for role in roles:
            if role not in user_roles:
                continue
            for i in range(len(parsed)):
                if(role.name == parsed[i] and role.name != 'Admin' and role.name != 'Bot'):
                    await client.send_message(message.channel, 'Removing ' + message.author.name + ' from ' + parsed[i] + '...')
                    await client.remove_roles(message.author, role)


    elif(message.content.startswith('!help')):
        s = """ ```Markdown
!help - Displays this message
!addgame [game] <game> <game> ... - Add the game role(s) to allow access to the chat channels
!removegame [game] <game> <game> ... - Remove the game role(s)

We support @overwatch, @league, @smash, @rocketleague, @heroes, @starcraft, and @hearthstone
```

        """
        await client.send_message(message.channel, s)


@client.event
async def on_ready():
    global roles, server
    server = client.get_server(server)
    roles = server.roles
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run('MzQ5NTk5MzA3MjAyMDM1NzE0.DH36AA.OpWuFqLsT35zjaeawqiv5bUJFzY')
