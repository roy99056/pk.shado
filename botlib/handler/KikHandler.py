from kik import KikApi, Configuration
from kik.messages import TextMessage, messages_from_json
import json


class KikHandler():
    def __init__(self, bot_username: str, bot_api_key: str):
        self.bot_username = bot_username
        self.bot_api_key = bot_api_key
        self.kik_instance = KikApi(self.bot_username, self.bot_api_key)

    def verify_signature(self, signature, data):
        return self.kik_instance.verify_signature(signature, data)

    def get_message(self, messages):
        print(type(messages))
        parsed_messages = messages_from_json(messages)

        for message in parsed_messages:
            if isinstance(message, TextMessage):
                return (message.from_user, message.chat_id, message.body)
            else:
                return (False, False, False)

    def send_message(self, to, chat, message):
        self.kik_instance.send_messages([
            TextMessage(
                to=to,
                chat_id=chat,
                body=message
            )
        ])

    def set_endpoint(self, webhook):
        self.kik_instance.set_configuration(Configuration(webhook=webhook))
        print('Starting BOT listener on ' + webhook)
