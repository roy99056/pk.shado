import json
import random
import string
import re
import sys
import discord
import logging
import time

from dice_roller.DiceThrower import DiceThrower


dice_expression = re.compile(r"(?:\[)([\w_:+-,<>=()]+)(?:\])?")
coin_expression = re.compile(r"(?:\[)(coin)")
room_expression = re.compile(r"(?:\[)(room)")

dice = DiceThrower()
root = logging.getLogger('bot')
client = discord.Client()

def main():

    # load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    DISCORD_BOT_TOKEN = config['DISCORD_BOT_TOKEN']

    # configure our logger
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

    client.run(DISCORD_BOT_TOKEN)


@client.async_event
def on_ready():
    root.info('Logged in as %s, id: %s', client.user.name, client.user.id)


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    await client.change_presence(game=discord.Game(name='RNG the Game'))
    if client.user in message.mentions:
        directed = True
        root.info('Directed Message Received')
        AT_BOT = "<@" + client.user.id + ">"
        plain_message = message.content[len(AT_BOT):]
    else:
        directed = False
        plain_message = message.content

    plain_message = plain_message.lower().strip(string.whitespace)

    dice_message = dice_expression.match(plain_message)
    coin_message = coin_expression.match(plain_message)
    room_message = room_expression.match(plain_message)

    if coin_message:
        await client.send_typing(message.channel)
        msg = random.choice(['heads', 'tails'])
        await client.send_message(message.channel, msg)

    elif room_message:
        await client.send_typing(message.channel)
        members = client.get_all_members()
        actives = []
        for member in members:
            if str(member.status) == "online":
                actives.append(member)
        member = random.choice(actives)

        msg = "I choose " + str(member.display_name)

        await client.send_message(message.channel, msg)

    elif dice_message:
        await client.send_typing(message.channel)
        trim_msg = dice_message.group(1)
        msg = get_dice(trim_msg)
        if not msg:
            msg = 'Unable to parse input'
        await client.send_message(message.channel, msg)
    return


def get_dice(command):
    root.info('Received Command %s', command)

    # apply template
    if command[0].isalpha():
        root.info('Template Format %s Received', command)
        template = re.match(r"([A-Za-z]+)([0-9+,]*)", command)
        if template:
            command = apply_template(template.group(1), template.group(2))

    if command is False:
        return None

    # get output format
    result_template = str()
    if "|" in command:
        command, result_template = command.split("|", 1)

    root.info('Formatted Command %s',command)
    score = dice.throw(command)

    if (len(result_template) > 0):
        msg = result_template.format(s=score)
    else:
        msg = score

    return msg


def apply_template(template, value=''):
    root.info('Template Parsed to %s %s', template, value)
    return {
        'sr': value + 'd6>=5f=1|{s[modified]} {s[success]} successes {s[fail]} fail',
        'f': '4d3-2' + value + '|{s[total]}',
        'w': '2d6+0' + value + '|{s[total]}'
    }.get(template, False)


if __name__ == '__main__':
    main()
