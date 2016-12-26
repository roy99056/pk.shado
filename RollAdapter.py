from __future__ import unicode_literals
from datetime import datetime
from chatterbot.logic.logic_adapter import LogicAdapter



class RollAdapter(LogicAdapter):

    def __init__(self, **kwargs):
        super(RollAdapter, self).__init__(**kwargs)

    def process(self, statement):
        from chatterbot.conversation import Statement
        from botlib.processor.DiceRoller import DiceRoller

        word_list = statement.text.split()

        try:
            if word_list[0].lower() == 'roll':
                dice = DiceRoller(word_list[1])
            else:
                return 0, Statement('')

            if dice.result:
                return 1, Statement(dice.get_result())
            else:
                return 0, Statement('')
        except:
            return 0, Statement('')