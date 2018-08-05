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

from card_picker.Deck import Deck
from card_picker.Card import *

from dice_roller.DiceThrower import DiceThrower

from flipper.Tosser import Tosser
from flipper.Casts import *

# set a few vars
root = logging.getLogger('bot')
LANGUAGE = "english"
SENTENCES_COUNT = 2
startup_extensions = ["Anime"]

bot = commands.Bot(
    command_prefix='!',
    description='A bot for gaming, and maybe anime?'
)

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

    for extension in startup_extensions:
        try:
            bot.load_extension('cogs.'+extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    bot.run(DISCORD_BOT_TOKEN)


def get_message(message, full_command, count, role, args):
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
        return '🎴 Card Hand ' + card_type[0].upper() + card_type[1:], hand

    elif role == 'c':
        tosser = Tosser(Coin)
        result = tosser.toss(count)
        return '⭕ Coin Flip', result

    elif role == 'e':
        tosser = Tosser(EightBall)
        result = tosser.toss(count)
        return '🎱 Eightball', result

    elif role == 'k':
        tosser = Tosser(Killer)
        result = tosser.toss(count)
        return '🗡 Killers', result

    elif role == 'r':
        members = message.server.members
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
        return '👥 Members', bag

    elif role == 'd':
        msg = DiceThrower().throw(full_command)
        if msg['natural'] == msg['modified']:
            msg.pop('modified', None)
        return '🎲 Dice Roll', msg

    else:
        root.info("Unknown role " + role)
        return


def apply_template(template, value=''):
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
            root.info('parsed template:%s value:%s', template_message.group(1), template_message.group(2))
            plain_message = reformed_message

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
        title, result = get_message(message, command_message.group(1), int(command_message.group(2)), command_message.group(3),
                                    command_message.group(4))

        # apply a template to the result (if requested)
        result_template = command_message.group(5)
        if len(result_template) > 0:
            msg = result_template.format(s=result)
        else:
            msg = result

    # if no command, generate a (useless?) response
    elif not command_message and (directed or message.channel.is_private):
        root.info('Plain text response.')
        msg = "I do not understand directed commands, please use the ![command] syntax."

    else:
        await bot.process_commands(message)
        return

    embed = discord.Embed(
        title=title
    )

    if isinstance(msg, list):
        embed.description = "\n".join(str(x) for x in msg)
    elif isinstance(msg,dict):
        for k, v in msg.items():
            embed.add_field(name=k, value=v, inline=False)
    else:
        embed.description = msg

    await bot.send_message(message.channel, embed=embed)


@bot.event
async def on_ready():
    root.info('Logged in as %s, id: %s', bot.user.name, bot.user.id)


@bot.event
async def on_server_join(server):
    root.info('Bot joined: %s', server.name)


@bot.event
async def on_server_remove(server):
    root.info('Bot left: %s', server.name)


@bot.event
async def on_command_completion(self, ctx):
    root.info('parsed command:%s', ctx.message.content)


@bot.command(pass_context=True)
async def vcr(ctx, amount: int):
    # First getting the voice channel object
    voice_channel = ctx.message.author.voice_channel
    if not voice_channel:
        return await bot.say("That is not a valid voice channel.")
    members = voice_channel.voice_members
    if len(members) < amount:
        return await bot.say("Sample larger than population.")
    member_names = [x.display_name for x in members]
    msg = random.sample(member_names, int(amount))

    embed = discord.Embed(
        title="{} random users from {}".format(str(amount), voice_channel.name),
        description="\n".join(str(x) for x in msg)
    )
    return await bot.say(embed=embed)


@bot.command(pass_context=True)
async def killbot(ctx):
    print("Shutting down!")
    await bot.say("Shutting down.")
    await bot.close()




if __name__ == '__main__':
    main()
