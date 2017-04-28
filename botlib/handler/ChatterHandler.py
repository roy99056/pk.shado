from chatterbot import ChatBot

# the point of this class is to handle incoming messages
# and return the response


class ChatterHandler():

    def __init__(self):
        self.bot = self.build_bot()

    def respond(self, message):
        return self.bot.get_response(message).text

    def build_bot(self):
        bot = ChatBot(
            'KIK',
            storage_adapter="chatterbot.storage.JsonFileStorageAdapter",
            logic_adapters=[
                {
                    'import_path': 'chatterbot_dice.RollAdapter'
                },
                "chatterbot.logic.MathematicalEvaluation"
            ],
            database="learning.db"
        )

        return bot
