from flask import Flask, render_template, request, jsonify, session
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# إعدادات تليجرام
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_code', methods=['POST'])
def send_code():
    phone = request.form.get('phone')
    session['phone'] = phone
    
    try:
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        client.connect()
        
        if not client.is_user_authorized():
            sent_code = client.send_code_request(phone)
            session['phone_code_hash'] = sent_code.phone_code_hash
            
            return jsonify({
                'status': 'success',
                'message': 'تم إرسال كود التحقق',
                'next_step': 'verify_code'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'حدث خطأ: {str(e)}'
        })

@app.route('/verify_code', methods=['POST'])
def verify_code():
    code = request.form.get('code')
    phone = session.get('phone')
    phone_code_hash = session.get('phone_code_hash')
    
    try:
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        client.connect()
        
        if not client.is_user_authorized():
            try:
                client.sign_in(phone, code, phone_code_hash=phone_code_hash)
            except Exception as e:
                if "two-step verification" in str(e):
                    return jsonify({
                        'status': '2fa_required',
                        'message': 'يطلب حسابك التحقق بخطوتين'
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': f'كود التحقق غير صحيح: {str(e)}'
                    })
        
        # إذا وصلنا هنا، تم تسجيل الدخول بنجاح
        session_string = client.session.save()
        
        # إرسال الجلسة إلى الرسائل المحفوظة
        client.send_message('me', f'تم استخراج الجلسة بواسطة @Tepthon\n\n{session_string}')
        
        return jsonify({
            'status': 'success',
            'message': 'تم استخراج الجلسة بنجاح وإرسالها إلى رسائلك المحفوظة'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'حدث خطأ: {str(e)}'
        })

@app.route('/verify_2fa', methods=['POST'])
def verify_2fa():
    password = request.form.get('password')
    phone = session.get('phone')
    
    try:
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        client.connect()
        
        if not client.is_user_authorized():
            client.sign_in(password=password)
            
            # إذا وصلنا هنا، تم تسجيل الدخول بنجاح
            session_string = client.session.save()
            
            # إرسال الجلسة إلى الرسائل المحفوظة
            client.send_message('me', f'تم استخراج الجلسة بواسطة @Tepthon\n\n{session_string}')
            
            return jsonify({
                'status': 'success',
                'message': 'تم استخراج الجلسة بنجاح وإرسالها إلى رسائلك المحفوظة'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'كلمة المرور غير صحيحة: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True)
