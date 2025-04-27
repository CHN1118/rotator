import os
import threading

from database.config import TOR_HS_FPATH, CHECK_TIME
from database.connection import init_db, with_cursor
from flask_main import create_app
from onion_loader.loader import scan_fonion_dirs
from pkg.rotation_training import countdown_half_rotator_once, rotator_loop
from tor.create_ronion import create_ronion, deactivate_expired_onions, clean_fully_expired_onions
from tor.rotator_utils import generate_irreversible_string, add_hidden_service

app = create_app()

def hhhh():
    print("创建动态.onion")

# 创建固定地址
def creat_fonion():
    result = generate_irreversible_string(12)
    onion_path1 = os.path.join(TOR_HS_FPATH, f"f_o{result}")
    add_hidden_service(onion_path1, 80, '127.0.0.1', 8080)
    with_cursor(scan_fonion_dirs)

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        init_db()
        # threading.Thread(target=countdown_half_rotator_once, args=(creat_fonion,), daemon=True).start()
        # 动态创建.onion
        threading.Thread(target=rotator_loop, args=(create_ronion,),daemon=True).start()
        # 检测处理过期的地址
        threading.Thread(target=rotator_loop, args=(deactivate_expired_onions,),daemon=True).start()
        # 12小时清理过期的文件
        threading.Thread(target=rotator_loop, args=(clean_fully_expired_onions,CHECK_TIME),daemon=True).start()
        print("✅ 初始化流程完成，开始监听 8080")
        with_cursor(scan_fonion_dirs)

    # app.run() 不能放到 if 内！

    app.run(debug=True, host="0.0.0.0", port=8080)


