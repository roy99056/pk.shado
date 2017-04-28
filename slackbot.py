import os
import time
from slackclient import SlackClient
from botlib.handler.ChatterHandler import ChatterHandler

import json

# get our config
with open('config.json', 'r') as f:
    config = json.load(f)

# ID as an environment variable
SLACK_BOT_ID = config['SLACK_BOT_ID']
SLACK_BOT_TOKEN = config['SLACK_BOT_TOKEN']

chatter = ChatterHandler()

# constants
AT_BOT = "<@" + SLACK_BOT_ID + ">"
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
            if output and 'text' in output and output['user'] != SLACK_BOT_ID and AT_BOT in output['text']:
                msg = output['text'][len(AT_BOT):]
                # return text after the @ mention, whitespace removed
                print("INPUT: " + msg)
                response = chatter.respond(msg)
                print("OUTPUT: " + response)
                slack_client.api_call("chat.postMessage", channel=output['channel'],
                        text=response, as_user=True)


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("ChatterBot connected and running!")
        while True:
            parse_slack_output(slack_client.rtm_read())
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
