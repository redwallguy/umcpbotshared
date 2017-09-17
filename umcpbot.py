import discord
import asyncio

client = discord.Client()
#test server variables
roles = []
renamed_channels = {}

@client.event
async def on_message(message):
    parsed = message.content.split()
    user_roles = message.author.roles

    if(message.content.startswith('!addgame')):
        parsed = [x.lower() for x in list(set(parsed[1:]))]
        if(message.channel.id != rolerequest):
            await client.send_message(message.channel, 'Keep all role requests in the <#' + rolerequest + '> channel!')
            return

        for role in roles:
            if role in user_roles:
                continue
            for i in range(len(parsed)):
                if(role.name == parsed[i] and role.name != 'Admin' and role.name != 'Bot'):
                    await client.send_message(message.channel, 'Adding ' + message.author.name + ' to ' + parsed[i] + '...')
                    await client.add_roles(message.author, role)

    if(message.content.startswith('!removegame')):
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


    elif(message.content.startswith('!help')):
        s = """ ```Markdown\n!help - Displays this message\n"""
        s = s + """!addgame [game] <game> <game> ... - Add the game role(s) to allow access to the chat channels\n"""
        s = s + """!removegame [game] <game> <game> ... - Remove the game role(s)\n\nWe support """
        for role in roles[1:-1]:
            if role.name != "Admin" and role.name != "Games Board" and role.name != "Bot":
                s = s + "@" + role.name + ","
        s = s + " and @" + roles[-1].name
        s = s + """\n```"""
        await client.send_message(message.channel, s)


@client.event
async def on_ready():
    global roles, server
    print(client.servers)
    server = list(client.servers)[0]
    roles = server.roles
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')




client.run('MzQ5NTk5MzA3MjAyMDM1NzE0.DH36AA.OpWuFqLsT35zjaeawqiv5bUJFzY')
