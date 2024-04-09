import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request

from message_processor import MessageProcessor

app = Flask(__name__)

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN')

IS_TESTING = os.getenv('IS_TESTING', 'false').lower() in ['true', '1', 't', 'y', 'yes']
LOCAL_DEV_URL = os.getenv('LOCAL_DEV_URL', '').strip()

message_processor = MessageProcessor()


def forward_to_local_dev(req):
    if not LOCAL_DEV_URL:
        return "LOCAL_DEV_URL is not set", 500
    local_dev_url = f'{LOCAL_DEV_URL}/test/webhook'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(local_dev_url, headers=headers, data=req.data)
    print(f"Forwarded to local dev url {local_dev_url} with status code: {response.status_code}")


@app.before_request
def before_request():
    if IS_TESTING and LOCAL_DEV_URL and request.path == '/webhook':
        forward_to_local_dev(request)


@app.route('/')
def home():
    return "Audio Transcription Running", 200


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and verify_token == WEBHOOK_VERIFY_TOKEN:
            print('Webhook verified')
            return challenge, 200
        return 'Webhook verification failed', 403

    elif request.method == 'POST':
        data = request.json
        result = message_processor.process_webhook_post_request(data)

        return jsonify(result)


@app.route('/test/webhook', methods=['POST'])
def test():
    data = request.json
    result = message_processor.process_webhook_post_request(data, debug=True)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
