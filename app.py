from flask import render_template
from flask import Flask, request, jsonify, render_template
from telethon import TelegramClient
from telethon.sessions import StringSession
import os
import asyncio

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/send-code", methods=["POST"])
def send_code():
    data = request.json
    phone = data.get("phone")
    api_id = int(data.get("api_id"))
    api_hash = data.get("api_hash")

    async def run():
        async with TelegramClient(StringSession(), api_id, api_hash) as client:
            result = await client.send_code_request(phone)
            return result.phone_code_hash

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        phone_code_hash = loop.run_until_complete(run())
        return jsonify({"status": "ok", "phone_code_hash": phone_code_hash})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@app.route("/verify-code", methods=["POST"])
def verify_code():
    data = request.json
    phone = data.get("phone")
    api_id = int(data.get("api_id"))
    api_hash = data.get("api_hash")
    code = data.get("code")
    phone_code_hash = data.get("phone_code_hash")
    password = data.get("password", None)

    async def run():
        async with TelegramClient(StringSession(), api_id, api_hash) as client:
            if password:
                await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash, password=password)
            else:
                await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
            return client.session.save()

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        session = loop.run_until_complete(run())
        return jsonify({"status": "ok", "session": session})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
