
from flask import Flask, request, jsonify, render_template
from telethon import TelegramClient
from telethon.sessions import StringSession
import os
import asyncio

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route('/send-code', methods=['POST'])
def send_code():
    data = request.json
    phone = data.get('phone')
    api_id = int(data.get('api_id'))
    api_hash = data.get('api_hash')

    async def send_code_async():
        async with TelegramClient(StringSession(), api_id, api_hash) as client:
            sent = await client.send_code_request(phone)
            return sent.phone_code_hash

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        phone_code_hash = loop.run_until_complete(send_code_async())
        return jsonify({'status': 'code_sent', 'phone_code_hash': phone_code_hash})
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
    phone_code_hash = data.get('phone_code_hash')

    async def verify_code_async():
        async with TelegramClient(StringSession(), api_id, api_hash) as client:
            if password:
                await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash, password=password)
            else:
                await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
            session_string = client.session.save()
            return session_string

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        session_string = loop.run_until_complete(verify_code_async())
        return jsonify({'session': session_string})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
