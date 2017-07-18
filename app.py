from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import json
import logging
import random
import re
import string
import sys

import discord
from card_picker.Deck import Deck
from dice_roller.DiceThrower import DiceThrower

# set a few vars
dice = DiceThrower()
root = logging.getLogger('bot')
client = discord.Client()
LANGUAGE = "english"
SENTENCES_COUNT = 2


# https://regex101.com/r/SrVpEg/2
# some base classes


def main():
    # load config
    with open('config.json', 'r') as f:
        config = json.load(f)

    # configure discord
    DISCORD_BOT_TOKEN = config['DISCORD_BOT_TOKEN']

    # configure our logger
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

    client.run(DISCORD_BOT_TOKEN)


def get_message(full_command, count, role, args):
    if role == 'h':
        if len(args) > 0:
            deck = Deck(args)
        else:
            deck = Deck('standard')
        deck.create()
        deck.shuffle()
        hand = deck.deal(count)
        return hand

    elif role == 'c':
        x = 1
        bag = []
        while x <= int(count):
            bag.append(random.choice(['heads', 'tails']))
            x += 1
        return bag

    elif role == 'r':
        members = client.get_all_members()
        actives = []
        for member in members:
            if str(member.status) == "online" and str(member.display_name) != client.user.name:
                actives.append(member)
        x = 1
        bag = []
        random.shuffle(actives)
        while x <= int(count) and len(actives) > 0:
            bag.append(actives.pop().display_name)
            x += 1
        return bag

    elif role == 'd':
        msg = dice.throw(full_command)
        return msg

    return ''


def apply_template(template, value=''):
    root.info('parsed template:%s value:%s', template, value)
    return {
        'sd': '!' + value + 'd6>=5f=1|{s[modified]} {s[success]} successes {s[fail]} fail',
        'st': '!' + value + 'hshadow',
        'f': '!' + '4d3-2' + value + '|{s[total]}',
        'w': '!' + '2d6+0' + value + '|{s[total]}'
    }.get(template, False)


@client.async_event
def on_ready():
    root.info('Logged in as %s, id: %s', client.user.name, client.user.id)


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    await client.change_presence(game=discord.Game(name='RNG the Game'))

    # remove bot from message if included (in @botname scenario)
    if client.user in message.mentions:
        directed = True
        AT_BOT = "<@" + client.user.id + ">"
        plain_message = message.content[len(AT_BOT):]
    else:
        directed = False
        plain_message = message.content

    # simplify the message format
    plain_message = plain_message.lower().strip(string.whitespace)

    # expressions
    command_expression = re.compile(r"(?:!)(([0-9]+)(d|c|r|h)([\w_:+\-,<>=()]*))(?:\|)?([\w{}\[\] ]*)")
    template_expression = re.compile(r"(?:!)([A-Za-z]+)([0-9+,]*)")

    # check if a template needs applied
    template_message = template_expression.match(plain_message)
    if template_message:
        reformed_message = apply_template(template_message.group(1), template_message.group(2))
        if reformed_message:
            plain_message = reformed_message
            reformed_message = True

    # convert the message to our command format
    command_message = command_expression.match(plain_message)

    # execute the request
    if command_message:
        root.info("parsed command "
                  + "Count:" + command_message.group(2)
                  + " Role:" + command_message.group(3)
                  + " Args:" + command_message.group(4)
                  + " Template:" + command_message.group(5))

        await client.send_typing(message.channel)
        result = get_message(command_message.group(1), int(command_message.group(2)), command_message.group(3),
                             command_message.group(4))

        # apply a template to the result (if requested)
        result_template = command_message.group(5)
        if (len(result_template) > 0):
            msg = result_template.format(s=result)
        else:
            msg = result

    # if no command, generate a (useless?) response
    elif not command_message and not template_message and (directed or message.channel.is_private):
        root.info('Plain text response.')
        msg = 'I do not understand.'
    else:
        return

    await client.send_message(message.channel, msg)


if __name__ == '__main__':
    main()
