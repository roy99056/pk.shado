import json
import re

import discord
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

    expression = re.match(r"(?:\[|\?)([\w_:+-,<>=]+)(?:\])?", message.content)
    if expression:
        msg = expression.group(1)
        print('Matches')
        msg = get_dice(msg)
        await client.send_message(message.channel, msg)

    elif client.user in message.mentions:
        print('Directed')
        AT_BOT = "<@" + client.user.id + ">"
        trim_msg = message.content[len(AT_BOT):]

        msg = get_dice(trim_msg)
        await client.send_message(message.channel, msg)

    return


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


def get_dice(command):
    print(command)
    # apply template
    if command[0].isalpha():
        print('Starts with a template name ' + command)
        template = re.match(r"([A-Za-z]+)([0-9+,]*)", command)
        if template:
            command = apply_template(template.group(1), template.group(2))

    # get output format
    result_template = str()
    if "|" in command:
        command, result_template = command.split("|", 1)

    print(command)
    score = dice.throw(command)

    if (len(result_template) > 0):
        msg = result_template.format(s=score)
    else:
        msg = score

    return msg


def apply_template(template, value=''):
    print(template, value)
    return {
        'SR': value + 'd6>=5f=1|{s[modified]} {s[success]} successes {s[fail]} fail',
        'F': '4d3-2' + value + '|{s[total]}',
        'W': '2d6+0' + value + '|{s[total]}'
    }.get(template, False)


client.run(DISCORD_BOT_TOKEN)
