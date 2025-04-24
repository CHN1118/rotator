import time

from database.config import ROTATOR_TIME


# 定时器 定时执行轮换任务
def rotator_loop(do_something_func):
    while True:
        print("🌀 轮换器任务执行中...")  # 你可以在这里执行你的 onion 添加、数据库写入等
        # 在这里放置你的实际逻辑，比如生成新的 .onion 地址等
        do_something_func()

        time.sleep(ROTATOR_TIME)


# 半周期轮换器
def countdown_half_rotator_once(do_something_func):
    interval = ROTATOR_TIME // 2
    print("🚀 初始调用")
    do_something_func()

    print(f"⌛ 倒计时 {interval} 秒...")
    time.sleep(interval)

    print("🔁 倒计时结束，执行第二次")
    do_something_func()

    print("✅ countdown_half_rotator_once 执行完成")