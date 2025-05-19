
from flask import Flask, request, jsonify, render_template
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send-code", methods=["POST"])
def send_code():
    data = request.json
    phone = data["phone"]
    api_id = int(data["api_id"])
    api_hash = data["api_hash"]

    async def main():
        async with TelegramClient(StringSession(), api_id, api_hash) as client:
            result = await client.send_code_request(phone)
            return result.phone_code_hash

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        phone_code_hash = loop.run_until_complete(main())
        return jsonify({"phone_code_hash": phone_code_hash})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/verify-code", methods=["POST"])
def verify_code():
    data = request.json
    phone = data["phone"]
    api_id = int(data["api_id"])
    api_hash = data["api_hash"]
    code = data["code"]
    phone_code_hash = data["phone_code_hash"]
    password = data.get("password", None)

    async def main():
        async with TelegramClient(StringSession(), api_id, api_hash) as client:
            await client.connect()
            if password:
                await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash, password=password)
            else:
                await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
            return client.session.save()

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        session = loop.run_until_complete(main())
        return jsonify({"session": session})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
