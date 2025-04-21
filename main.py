from flask import Flask, render_template, session, send_from_directory, request, redirect, url_for
import uuid
from captcha_generator import generate_captcha_text, generate_captcha_image
from datetime import datetime
from database.connection import get_connection, with_cursor
from database.models.fixed_onion import create_fixed_onion_table
from database.models.request_logs import create_request_logs_table
from database.models.rotating_onion import create_rotating_onion_table
from onion_loader.loader import scan_onion_dirs
app = Flask(__name__)

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

conn = get_connection()
if conn:
    cursor = conn.cursor()
    cursor.execute("SELECT NOW()")
    print("✅ 当前时间：", cursor.fetchone())
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
    init_db()
    with_cursor(scan_onion_dirs)
    # create_rotator_onion()
    # with_cursor(create_rotating_onion)
    # onion_info = create_ephemeral_onion_and_store()
    app.run(debug=True, host="0.0.0.0", port=8080)
