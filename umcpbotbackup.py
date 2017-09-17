import discord
import asyncio

client = discord.Client()
#test server variables
server = '349777729861976064'
rolerequest = '349777729861976065'
#release server variables
server = '348919724635324419'
rolerequest = '349781614877999104'
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
        s = """ ```Markdown
!help - Displays this message
!addgame [game] <game> <game> ... - Add the game role(s) to allow access to the chat channels
!removegame [game] <game> <game> ... - Remove the game role(s)

We support @overwatch, @league, @smash, @rocketleague, @heroes, @starcraft, @hearthstone, @csgo, @pubg, and @destiny
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

async def update_gamelobby_name(channel, members):
    member_roles = {}
    for member in members:
        for role in member.roles:
            if not role.is_everyone:
                if role in member_roles:
                    member_roles[role] = member_roles[role] + 1
                else:
                    member_roles[role] = 1

    max_role = max(member_roles, key=lambda k: member_roles[k])
    await client.edit_channel()

@client.event
async def on_voice_state_update(before, after):
    if(after.voice.voice_channel is not None):
        members = after.voice.voice_channel.voice_members
        await update_gamelobby_name(after.voice.voice_channel, members)

    if(before.voice.voice_channel is not None):
        members = before.voice.voice_channel.voice_members
        id = before.voice.voice_channel.id
        if (len(members) == 0 and renamed_channels.has_key(id)):
            await client.edit_channel(before.voice.voice_channel, name=renamed_channels[id])
            renamed_channel.pop(id)
        else
            await update_gamelobby_name(before.voice.voice_channel, members)



client.run('MzUyNTAzNDI5ODkwOTY1NTE0.DKBn5Q.uzxPgF-95GSZyXvzYKrAIDoi0c8')
