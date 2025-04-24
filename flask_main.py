import os

from flask import Flask, render_template, session, request
from verification.captcha_generator import generate_captcha_text, generate_captcha_image
import uuid
from datetime import datetime
from verification.captcha_generator import generate_captcha_text


def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    init_flask_server(app)
    return app

# flask服务

def init_flask_server(app: Flask):
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

    print("✅ Flask 路由已成功注册")







