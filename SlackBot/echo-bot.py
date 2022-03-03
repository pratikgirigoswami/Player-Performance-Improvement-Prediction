from distutils.log import debug
from email import message
import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter

load_dotenv()
print(os.environ['SIGNING_SECRET'])
app = Flask(__name__)

# Object to handle the events
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

BOT_ID = client.api_call('auth.test')['user_id']

@slack_event_adapter.on('message')
def message(payload):
    # print(payload)
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    if user_id != BOT_ID:
        client.chat_postMessage(channel=channel_id, text=text)
    
    
@app.route('/command/echo', methods=['POST'])
def echo():
    data = request.form
    # print(data)
    channel_id = data.get('channel_id')
    text = data.get('text')
    client.chat_postMessage(channel=channel_id, text=text)

    return Response(), 200


if __name__ == "__main__":
    app.run(debug=True)