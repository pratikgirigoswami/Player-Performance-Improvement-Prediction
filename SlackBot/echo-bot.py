from distutils.log import debug
from email import message
import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
# Object to handle the events
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'],'/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
# client.chat_postMessage(channel='#test-echo-bot', text='Hello')

BOT_ID = client.api_call('auth.test')['user_id']

@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    if user_id != BOT_ID:
        client.chat_postMessage(channel=channel_id, text=text)
    
    



if __name__ == "__main__":
    app.run(debug=True)