import os
import time
from slackclient import SlackClient
from chatterbot import ChatBot


# ID as an environment variable
BOT_ID = "U3EF5TTGU"
SLACK_BOT_TOKEN = "xoxb-116515945572-EKzCYimtFExstOeNErcNnEDc"

# Bot
# configure the bot
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
bot.train()

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

# instantiate Slack & Twilio clients
slack_client = SlackClient(SLACK_BOT_TOKEN)

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and output['user'] != BOT_ID : # and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                slack_client.api_call("chat.postMessage", channel=output['channel'], 
                        text=bot.get_response(output['text']).text, as_user=True)


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("ChatterBot connected and running!")
        while True:
            parse_slack_output(slack_client.rtm_read())
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
