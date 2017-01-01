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
            trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
            storage_adapter="chatterbot.storage.JsonFileStorageAdapter",
            logic_adapters=[
                {
                    'import_path': 'chatterbot_dice.RollAdapter'
                },
                "chatterbot.logic.MathematicalEvaluation",
                "chatterbot.logic.BestMatch",
                {
                    'import_path': 'chatterbot_markov.MarkovAdapter',
                    'threshold': 0.6,
                    'default_response': 'I am sorry, but I do not understand.'
                }
            ],
            database="learning.db"
        )
        # Train based on the english corpus
        bot.train("chatterbot.corpus.english")

        return bot