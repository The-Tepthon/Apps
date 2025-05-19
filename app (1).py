
from flask import Flask, request, jsonify
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os

app = Flask(__name__)

@app.route('/send-code', methods=['POST'])
def send_code():
    data = request.json
    phone = data.get('phone')
    api_id = int(data.get('api_id'))
    api_hash = data.get('api_hash')

    session = StringSession()
    client = TelegramClient(session, api_id, api_hash)

    try:
        client.connect()
        client.send_code_request(phone)
        client.disconnect()
        return jsonify({'status': 'code_sent'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.json
    phone = data.get('phone')
    api_id = int(data.get('api_id'))
    api_hash = data.get('api_hash')
    code = data.get('code')
    password = data.get('password', None)

    session = StringSession()
    client = TelegramClient(session, api_id, api_hash)

    try:
        client.connect()
        if password:
            client.sign_in(phone, code, password=password)
        else:
            client.sign_in(phone, code)
        string_session = client.session.save()
        client.disconnect()
        return jsonify({'session': string_session})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
