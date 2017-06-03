import json

import ipgetter
from chatterbot import ChatBot
from flask import Flask, request, Response
from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage, SuggestedResponseKeyboard, TextResponse, StartChattingMessage


class KikBot(Flask):
    """ Flask kik bot application class"""

    # bot.get_response(str(messages)).text
    bot = ChatBot(
        'danger_bot',
        trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
        training_data='chatterbot.corpus.english',
        storage_adapter="chatterbot.storage.JsonFileStorageAdapter",
        logic_adapters=[
            "chatterbot.logic.MathematicalEvaluation",
            {
                'import_path': 'chatterbot.logic.BestMatch'
            },
            {
                'import_path': 'chatterbot_markov.MarkovAdapter',
                'threshold': 0.6,
                'default_response': 'I am sorry, but I do not understand.'
            }
        ],
        database="learning.db"
    )

    def __init__(self, kik_api, import_name, static_path=None, static_url_path=None, static_folder="static",
                 template_folder="templates", instance_path=None, instance_relative_config=False,
                 root_path=None):

        self.kik_api = kik_api

        super(KikBot, self).__init__(import_name, static_path, static_url_path, static_folder, template_folder,
                                     instance_path, instance_relative_config, root_path)

        self.route("/incoming", methods=["POST"])(self.incoming)

    def incoming(self):
        """Handle incoming messages to the bot. All requests are authenticated using the signature in
        the 'X-Kik-Signature' header, which is built using the bot's api key (set in main() below).
        :return: Response
        """
        # verify that this is a valid request
        if not self.kik_api.verify_signature(
                request.headers.get("X-Kik-Signature"), request.get_data()):
            return Response(status=403)

        messages = messages_from_json(request.json["messages"])

        response_messages = []

        for message in messages:
            user = self.kik_api.get_user(message.from_user)

            # Check if its the user's first message. Start Chatting messages are sent only once.
            if isinstance(message, StartChattingMessage):

                response_messages.append(TextMessage(
                    to=message.from_user,
                    chat_id=message.chat_id,
                    body="Hey {}, lets see if I can figure out this?".format(user.first_name)))

            # Check if the user has sent a text message.
            elif isinstance(message, TextMessage):
                user = self.kik_api.get_user(message.from_user)
                message_body = message.body.lower()

                response_messages.append(TextMessage(
                    to=message.from_user,
                    chat_id=message.chat_id,
                    body=self.bot.get_response(message_body).text))

            # If its not a text message, give them another chance to use the suggested responses
            else:

                response_messages.append(TextMessage(
                    to=message.from_user,
                    chat_id=message.chat_id,
                    body="Sorry, I didn't quite understand that. How are you, {}?".format(user.first_name),
                    keyboards=[SuggestedResponseKeyboard(responses=[TextResponse("Good"), TextResponse("Bad")])]))

            # We're sending a batch of messages. We can send up to 25 messages at a time (with a limit of
            # 5 messages per user).

            self.kik_api.send_messages(response_messages)

        return Response(status=200)


if __name__ == "__main__":
    # get our config
    with open('config.json', 'r') as f:
        config = json.load(f)

    # load and set up environment
    BOT_USERNAME = config['KIK_BOT_USERNAME']
    BOT_API_KEY = config['KIK_BOT_API_KEY']
    BOT_PORT = config['KIK_BOT_PORT']

    MY_IP = ipgetter.myip()

    YOUR_WEBHOOK = 'http://' + MY_IP + ':' + BOT_PORT + '/incoming'

    # initialize
    kik = KikApi(BOT_USERNAME, BOT_API_KEY)
    kik.set_configuration(Configuration(webhook=YOUR_WEBHOOK))

    app = KikBot(kik, __name__)
    app.run(host='0.0.0.0', port=BOT_PORT, debug=True, use_reloader=False)
