from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import json
import logging
import random
import re
import string
import sys
import discord

from discord.ext import commands
bot = commands.Bot(command_prefix='!')

from card_picker.Deck import Deck
from card_picker.Card import *

from dice_roller.DiceThrower import DiceThrower

from flipper.Tosser import Tosser
from flipper.Casts import *

# set a few vars
root = logging.getLogger('bot')
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

    bot.run(DISCORD_BOT_TOKEN)


def get_message(full_command, count, role, args):
    if role == 'h':
        card_conv = {
            'standard' : StandardCard,
            'shadow' : ShadowCard,
            'tarot' : TarotCard,
            'uno' : UnoCard
        }

        if len(args) > 0:
            card_type = args
        else:
            card_type = 'standard'

        cards = card_conv[card_type]
        deck = Deck(cards)
        deck.create()
        deck.shuffle()
        hand = deck.deal(count)
        return hand

    elif role == 'c':
        tosser = Tosser(Coin)
        result = tosser.toss(count)
        return result

    elif role == 'e':
        tosser = Tosser(EightBall)
        result = tosser.toss(count)
        return result

    elif role == 'k':
        tosser = Tosser(Killer)
        result = tosser.toss(count)
        return result


    elif role == 'r':
        members = bot.get_all_members()
        actives = []
        for member in members:
            if str(member.status) == "online" and str(member.display_name) != bot.user.name:
                actives.append(member)
        x = 1
        bag = []
        random.shuffle(actives)
        while x <= int(count) and len(actives) > 0:
            bag.append(actives.pop().display_name)
            x += 1
        return bag

    elif role == 'd':
        msg = DiceThrower().throw(full_command)
        return msg

    else:
        root.info("Unknown role " + role)
        return


def apply_template(template, value=''):
    root.info('parsed template:%s value:%s', template, value)
    return {
        'sd': '!' + value + 'd6>=5f=1|{s[modified]} {s[success]} successes {s[fail]} fail',
        'st': '!' + value + 'hshadow',
        'f': '!' + '4d3-2' + value + '|{s[total]}',
        'w': '!' + '2d6+0' + value + '|{s[total]}'
    }.get(template, False)


@bot.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return

    await bot.change_presence(game=discord.Game(name='RNG the Game'))

    # remove bot from message if included (in @botname scenario)
    if bot.user in message.mentions:
        directed = True
        AT_BOT = "<@" + bot.user.id + ">"
        plain_message = message.content[len(AT_BOT):]
    else:
        directed = False
        plain_message = message.content

    # simplify the message format
    plain_message = plain_message.lower().strip(string.whitespace)

    # expressions
    command_expression = re.compile(r"(?:!)(([0-9]+)(d|c|e|r|h|k)([\w_:+\-,<>=()]*))(?:\|)?([\w{}\[\] ]*)")
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

        await bot.send_typing(message.channel)
        result = get_message(command_message.group(1), int(command_message.group(2)), command_message.group(3),
                             command_message.group(4))

        # apply a template to the result (if requested)
        result_template = command_message.group(5)
        if len(result_template) > 0:
            msg = result_template.format(s=result)
        else:
            msg = result

    # if no command, generate a (useless?) response
    elif not command_message and not template_message and (directed or message.channel.is_private):
        root.info('Plain text response.')
        msg = "I do not understand."

    else:
        await bot.process_commands(message)
        return

    root.info('%s', msg)
    await bot.send_message(message.channel, msg)


@bot.event
async def on_ready():
    root.info('Logged in as %s, id: %s', bot.user.name, bot.user.id)


@bot.command(pass_context=True)
async def vcr(ctx, amount: int, voice_channel_id: str):
    # First getting the voice channel object
    voice_channel = discord.utils.get(ctx.message.server.channels, id = voice_channel_id)
    if not voice_channel:
        return await bot.say("That is not a valid voice channel.")

    members = voice_channel.voice_members
    member_names = [x.display_name for x in members]

    msg = random.sample(member_names, int(amount))
    embed = discord.Embed(title = "{} member(s) in {}".format(len(members), voice_channel.name),
                          description = member_names,
                          color=discord.Color.blue())

    return await bot.say(msg)


if __name__ == '__main__':
    main()
