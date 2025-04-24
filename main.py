import os
import uuid
from datetime import datetime

from flask import Flask, render_template, session, request

from verification.captcha_generator import generate_captcha_text, generate_captcha_image
from database.connection import get_connection, with_cursor
from database.models.fixed_onion import create_fixed_onion_table
from database.models.request_logs import create_request_logs_table
from database.models.rotating_onion import create_rotating_onion_table
from onion_loader.loader import scan_onion_dirs

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 生成随机密钥


# 初始化数据库
def init_db():
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    create_fixed_onion_table(cursor)
    create_rotating_onion_table(cursor)
    create_request_logs_table(cursor)
    print("✅ 数据库初始化完成")
    cursor.close()
    conn.close()


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
    # 只有 Flask 热重载的主进程才会执行
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        init_db()
        with_cursor(scan_onion_dirs)
        # result = generate_irreversible_string(12)
        # onion_path = os.path.join(TOR_HS_RPATH, f"r_o{result}")
        # onion_path1 = os.path.join(TOR_HS_FPATH, f"f_o{result}")
        # add_hidden_service(onion_path, 80, '127.0.0.1', 8080)
        # add_hidden_service(onion_path1, 80, '127.0.0.1', 8080)
        print("✅ 初始化流程完成，开始监听 8080")

    app.run(debug=True, host="0.0.0.0", port=8080)
