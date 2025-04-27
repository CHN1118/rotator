import time
import logging
from database.config import ROTATOR_TIME
import threading
from datetime import datetime
from database.connection import get_connection

lock = threading.Lock()

# 定时器 定时执行轮换任务
def rotator_loop(func,timeq=ROTATOR_TIME):
    while True:
        print("🌀 轮换器任务执行中...")  # 你可以在这里执行你的 onion 添加、数据库写入等
        with lock:
            try:
            # 在这里放置你的实际逻辑，比如生成新的 .onion 地址等
                func()
            except Exception as e:
                logging.error(f"Error in {func.__name__}: {e}")
        time.sleep(timeq)


# 半周期轮换器
def countdown_half_rotator_once(funcf,funcl):
    interval = ROTATOR_TIME // 2
    print("🚀 初始调用")
    funcf()

    print(f"⌛ 倒计时 {interval} 秒...")
    time.sleep(interval)

    print("🔁 倒计时结束，执行第二次")
    funcl()

    print("✅ countdown_half_rotator_once 执行完成")


def get_fixed_onions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT address, is_active FROM fixed_onion
        WHERE is_active = TRUE
        ORDER BY id ASC;
    """)
    onions = cursor.fetchall()
    cursor.close()
    conn.close()
    return onions


def get_rotating_onions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT address, expires_at, id FROM rotating_onion
        WHERE is_active = TRUE
        ORDER BY expires_at DESC
        LIMIT 2;
    """)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    rotating_onions = []
    for address, expires_at,  id in results:
        now = datetime.utcnow()
        delta = expires_at - now

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

        rotating_onions.append({
            'short_address': address[:5],
            'time_left': time_left,
            'status': status,
            'id': id
        })

    return rotating_onions