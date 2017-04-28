import json

import ipgetter
from celery import Celery
from flask import Flask, request, Response

from botlib.handler.KikHandler import KikHandler
from botlib.handler.ChatterHandler import ChatterHandler

# get our config
with open('config.json', 'r') as f:
    config = json.load(f)

# load and set up environment
BOT_USERNAME = config['KIK_BOT_USERNAME']
BOT_API_KEY = config['KIK_BOT_API_KEY']
BOT_PORT = config['KIK_BOT_PORT']

CELERY_BROKER_URL = config['CELERY_BROKER_URL']
CELERY_RESULT_BACKEND = config['CELERY_RESULT_BACKEND']

MY_IP = ipgetter.myip()
YOUR_WEBHOOK = 'http://' + MY_IP + ':' + BOT_PORT + '/incoming'

# initialize
kik = KikHandler(BOT_USERNAME, BOT_API_KEY)
kik.set_endpoint(YOUR_WEBHOOK)

chatter = ChatterHandler()

# celery builder
def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL=CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND
)
celery = make_celery(app)

@celery.task(name="tasks.build_message")
def build_message(messages):
    print(type(messages))
    sender, chat, message = kik.get_message(messages)
    print("INPUT: " + message)
    output = chatter.respond(message)
    print("OUTPUT: " + output)
    kik.send_message(sender, chat, output)

# main loop
@app.route('/incoming', methods=['POST'])
def incoming():
    print("incoming request")
    if not kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):
        return Response(status=403)
    print(type(request.json['messages']))
    launch = celery.send_task("tasks.build_message",[request.json['messages']])
    print(launch)
    return Response(status=200)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=BOT_PORT, debug=True, use_reloader=False)