from cogs.Utils import *

from discord.ext import commands
from dice_roller.DiceThrower import DiceThrower

from card_picker.Deck import Deck
from card_picker.Card import *

from flipper.Tosser import Tosser
from flipper.Casts import *

class Games:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def dice(self, ctx, roll='1d1'):
        msg = DiceThrower().throw(roll)
        print(msg)
        if type(msg) is dict:
            if msg['natural'] == msg['modified']:
                msg.pop('modified', None)
            title = '🎲 Dice Roll'
            embed = make_embed(title, msg)
            await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.say("Error parsing dice.")

    @commands.command(pass_context=True)
    async def card(self, ctx, card: str, count=1):
        card_conv = {
            'standard' : StandardCard,
            'shadow' : ShadowCard,
            'tarot' : TarotCard,
            'uno' : UnoCard
        }

        if len(card) > 0:
            card_type = card
        else:
            card_type = 'standard'

        cards = card_conv[card_type]
        deck = Deck(cards)
        deck.create()
        deck.shuffle()
        hand = deck.deal(count)
        if type(hand) is list:
            title = '🎴 Card Hand ' + card_type[0].upper() + card_type[1:]
            embed = make_embed(title, hand)
            await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.say("Error parsing dice.")

    @commands.command(pass_context=True)
    async def coin(self, ctx, count=1):
        tosser = Tosser(Coin)
        result = tosser.toss(count)
        if type(result) is list:
            title = '⭕ Coin Flip'
            embed = make_embed(title, result)
            await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.say("Error parsing coin.")

    @commands.command(pass_context=True)
    async def eightball(self, ctx, count=1):
        tosser = Tosser(EightBall)
        result = tosser.toss(count)
        if type(result) is list:
            title = '🎱 Eightball'
            embed = make_embed(title, result)
            await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.say("Error parsing coin.")

    @commands.command(pass_context=True)
    async def killer(self, ctx, count=1):
        tosser = Tosser(Killer)
        result = tosser.toss(count)
        if type(result) is list:
            title = '🗡 Killers'
            embed = make_embed(title, result)
            await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.say("Error parsing coin.")

    @commands.command(pass_context=True)
    async def defender(self, ctx, count=1):
        tosser = Tosser(Defender)
        result = tosser.toss(count)
        if type(result) is list:
            title = '🛡️ Defenders'
            embed = make_embed(title, result)
            await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.say("Error parsing defender.")

    @commands.command(pass_context=True)
    async def attacker(self, ctx, count=1):
        tosser = Tosser(Attacker)
        result = tosser.toss(count)
        if type(result) is list:
            title = '🔫 Attackers'
            embed = make_embed(title, result)
            await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.say("Error parsing attacker.")

def setup(bot):
    bot.add_cog(Games(bot))