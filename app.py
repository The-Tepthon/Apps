from flask import Flask, render_template, request, jsonify, session
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
RECAPTCHA_SECRET = os.getenv('RECAPTCHA_SECRET_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_code', methods=['POST'])
def send_code():
    phone = request.form.get('phone')
    recaptcha_token = request.form.get('g-recaptcha-response')

    if not recaptcha_token:
        return jsonify({'status': 'error', 'message': 'ظٹط±ط¬ظ‰ طھط£ظƒظٹط¯ ط£ظ†ظƒ ظ„ط³طھ ط±ظˆط¨ظˆطھظ‹ط§'})

    recaptcha_response = requests.post(
        'https://www.google.com/recaptcha/api/siteverify',
        data={
            'secret': RECAPTCHA_SECRET,
            'response': recaptcha_token
        }
    ).json()

    if not recaptcha_response.get('success'):
        return jsonify({'status': 'error', 'message': 'ظپط´ظ„ ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† reCAPTCHA'})

    session['phone'] = phone

    try:
                loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async def run():
            async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
            sent_code = client.send_code_request(phone)
            session['phone_code_hash'] = sent_code.phone_code_hash
        loop.run_until_complete(run())

        return jsonify({
            'status': 'success',
            'message': 'طھظ… ط¥ط±ط³ط§ظ„ ظƒظˆط¯ ط§ظ„طھط­ظ‚ظ‚',
            'next_step': 'verify_code'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'ط­ط¯ط« ط®ط·ط£: {str(e)}'
        })

@app.route('/verify_code', methods=['POST'])
def verify_code():
    code = request.form.get('code')
    phone = session.get('phone')
    phone_code_hash = session.get('phone_code_hash')

    try:
                loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async def run():
            async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
            try:
                client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        loop.run_until_complete(run())
            except Exception as e:
                if "two-step verification" in str(e).lower():
                    return jsonify({
                        'status': '2fa_required',
                        'message': 'ظٹط·ظ„ط¨ ط­ط³ط§ط¨ظƒ ط§ظ„طھط­ظ‚ظ‚ ط¨ط®ط·ظˆطھظٹظ†'
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'ط±ظ…ط² ط§ظ„طھط­ظ‚ظ‚ ط؛ظٹط± طµط­ظٹط­ ط£ظˆ ظ…ظ†طھظ‡ظٹ ط§ظ„طµظ„ط§ط­ظٹط©'
                    })

            session_string = client.session.save()
            client.send_message('me', f'طھظ… ط§ط³طھط®ط±ط§ط¬ ط§ظ„ط¬ظ„ط³ط© ط¨ظˆط§ط³ط·ط© @Tepthon\n\n{session_string}')
        loop.run_until_complete(run())

        return jsonify({
            'status': 'success',
            'message': 'طھظ… ط§ط³طھط®ط±ط§ط¬ ط§ظ„ط¬ظ„ط³ط© ط¨ظ†ط¬ط§ط­ ظˆط¥ط±ط³ط§ظ„ظ‡ط§ ط¥ظ„ظ‰ ط±ط³ط§ط¦ظ„ظƒ ط§ظ„ظ…ط­ظپظˆط¸ط©'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'ط­ط¯ط« ط®ط·ط£: {str(e)}'
        })

@app.route('/verify_2fa', methods=['POST'])
def verify_2fa():
    password = request.form.get('password')
    phone = session.get('phone')

    try:
                loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async def run():
            async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
            client.sign_in(phone=phone, password=password)
        loop.run_until_complete(run())

            session_string = client.session.save()
            client.send_message('me', f'طھظ… ط§ط³طھط®ط±ط§ط¬ ط§ظ„ط¬ظ„ط³ط© ط¨ظˆط§ط³ط·ط© @Tepthon\n\n{session_string}')
        loop.run_until_complete(run())

        return jsonify({
            'status': 'success',
            'message': 'طھظ… ط§ط³طھط®ط±ط§ط¬ ط§ظ„ط¬ظ„ط³ط© ط¨ظ†ط¬ط§ط­ ظˆط¥ط±ط³ط§ظ„ظ‡ط§ ط¥ظ„ظ‰ ط±ط³ط§ط¦ظ„ظƒ ط§ظ„ظ…ط­ظپظˆط¸ط©'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'ظƒظ„ظ…ط© ط§ظ„ظ…ط±ظˆط± ط؛ظٹط± طµط­ظٹط­ط©: {str(e)}'
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
