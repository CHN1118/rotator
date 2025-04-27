import time
import logging
from database.config import ROTATOR_TIME
import threading
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