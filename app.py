# app.py
from flask import Flask, render_template, session, send_from_directory, request, redirect, url_for
import os
import uuid
import ssl
from captcha_generator import generate_captcha_text, generate_captcha_image
from datetime import datetime

app = Flask(__name__)

# 加载证书
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain('cert.pem', 'key.pem')

app.secret_key = 'your-secret-key'
app.config['CAPTCHA_FOLDER'] = 'static/captcha'

@app.route('/')
def index():
    captcha_text = generate_captcha_text()
    session['captcha'] = captcha_text
    session['captcha_time'] = datetime.now().timestamp()  # 添加时间戳

    filename = f"{uuid.uuid4().hex}.png"
    generate_captcha_image(captcha_text, filename)
    return render_template('index.html', captcha_image=f'captcha/{filename}')

@app.route('/validate', methods=['POST'])
def validate():
    user_input = request.form.get('captcha_input', '')
    captcha_time = session.get('captcha_time')

    if captcha_time is None:
        return '❌ 验证码已过期，请刷新页面重试。'

    now = datetime.now().timestamp()
    if now - captcha_time > 60:
        return '❌ 验证码已过期，请刷新页面重试。'

    if user_input.upper() == session.get('captcha', ''):
        session.pop('captcha', None)
        session.pop('captcha_time', None)
        return '✅ 验证成功！你现在可以访问下一页了。'


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
    # app.run(debug=True, host="0.0.0.0", port=8080, ssl_context=context)
