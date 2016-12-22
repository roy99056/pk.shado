from flask import Flask, request, Response
import ipgetter
import json
import multiprocessing as mp

from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage

from chatterbot import ChatBot

app = Flask(__name__)

# main loop
@app.route('/incoming', methods=['POST'])
def incoming():
    if not kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):
        return Response(status=403)

    process_message(request.json['messages'])

    return Response(status=200)


def process_message(json_messages):
    messages = messages_from_json(json_messages)

    for message in messages:
        if isinstance(message, TextMessage):
            print(message.to)
            print(message.chat_id)
            print(message.body)
            print(message.keyboards)
            print(message.mention)
            print(message.delay)
            print(message.type_time)
            kik.send_messages([
                TextMessage(
                    to=message.from_user,
                    chat_id=message.chat_id,
                    body=bot.get_response(message.body).text
                )
            ])
        else:
            print(message)

    return True


def build_kik():
    # configure kik
    kik = KikApi(BOT_USERNAME, BOT_API_KEY)
    kik.set_configuration(Configuration(webhook=YOUR_WEBHOOK))
    
    return kik

def build_bot():

    bot = ChatBot(
        'KIK',
        trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
        storage_adapter="chatterbot.storage.JsonFileStorageAdapter",
        logic_adapters=[
            "chatterbot.logic.MathematicalEvaluation",
            "chatterbot.logic.BestMatch"
        ],
        database="learning.db"
    )
    # Train based on the english corpus
    bot.train("chatterbot.corpus.english")

    return bot


with open('config.json', 'r') as f:
    config = json.load(f)

# load and set up environment
MY_IP = ipgetter.myip()
BOT_USERNAME = config['BOT_USERNAME']
BOT_API_KEY = config['BOT_API_KEY']
BOT_PORT = config['BOT_PORT']
YOUR_WEBHOOK = 'http://' + MY_IP + ':' + BOT_PORT + '/incoming'

kik = build_kik()
bot = build_bot()

print('Starting BOT listener on ' + YOUR_WEBHOOK)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9009, debug=True, use_reloader=False)
