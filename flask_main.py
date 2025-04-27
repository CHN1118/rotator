import os

from flask import Flask, render_template, session, request, send_from_directory

from database.connection import get_connection
from pkg.rotation_training import get_fixed_onions, get_rotating_onions
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
    # @app.route('/')
    # def index():
    #     captcha_text = generate_captcha_text()
    #     session['captcha'] = captcha_text
    #     session['captcha_time'] = datetime.now().timestamp()  # 添加时间戳
    #
    #     filename = f"{uuid.uuid4().hex}.png"
    #     generate_captcha_image(captcha_text, filename)
    #     return render_template('index.html', captcha_image=f'captcha/{filename}')
    @app.route('/')
    def index():
        fixed_onions = get_fixed_onions()
        rotating_onions = get_rotating_onions()
        # print(rotating_onions)
        return render_template('index.html', fixed_onions=fixed_onions, rotating_onions=rotating_onions)

    @app.route('/signed.html')
    def signed():
        return send_from_directory('static', 'signed.html')

    @app.route('/onion/<int:onion_id>')
    def onion_detail(onion_id):
        # 从数据库中查找对应 ID 的 Onion 信息
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rotating_onion WHERE id = %s;", (onion_id,))
        onion = cursor.fetchone()
        print(onion)
        now = datetime.utcnow()
        delta = onion[4] - now
        seconds = int(delta.total_seconds())
        if seconds <= 0:
            time_left = "Expired"
            status = "rgba(255, 0, 0, 0.7)"
        elif seconds < 60:
            time_left = f"{seconds} seconds"
            status = "rgba(255, 0, 0, 0.7)"
        elif seconds < 300:
            minutes = seconds // 60
            time_left = f"{minutes} minutes"
            status = "rgba(255, 165, 0, 0.7)"
        else:
            minutes = seconds // 60
            time_left = f"{minutes} minutes"
            status = "rgba(0, 255, 0, 0.7)"
        onion = {
            'id': onion[0],
            'address': onion[1],
            'expires_at': time_left,
            'status': status,
            'is_active': onion[2],
        }
        cursor.close()
        conn.close()

        if onion:
            return render_template("onion_detail.html", onion=onion)
        else:
            return "Onion ID not found", 404

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







