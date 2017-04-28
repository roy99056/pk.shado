import discord

# from botlib.handler.ChatterHandler import ChatterHandler

import json
from dice_roller.DiceThrower import DiceThrower

with open('config.json', 'r') as f:
    config = json.load(f)

DISCORD_BOT_TOKEN = config['DISCORD_BOT_TOKEN']

client = discord.Client()
dice = DiceThrower()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('?'):
        print(message.content)
        # msg = chatter.respond(message.content[1:])
        msg = dice.throw(message.content[1:])
        await client.send_message(message.channel, msg)
    elif client.user in message.mentions:
        AT_BOT = "<@" + client.user.id + ">"
        trim_msg = message.content[len(AT_BOT):]
        print(AT_BOT)
        print(trim_msg)
        # msg = chatter.respond(trim_msg)
        msg = dice.throw(trim_msg)
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(DISCORD_BOT_TOKEN)
