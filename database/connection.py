import psycopg2
from database.config import DB_CONFIG
from database.models.fixed_onion import create_fixed_onion_table
from database.models.request_logs import create_request_logs_table
from database.models.rotating_onion import create_rotating_onion_table


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


# 连接数据库
def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        return conn
    except Exception as e:
        print("❌ 数据库连接失败：", e)
        return None

# 装饰器
def with_cursor(task_function):
    """
    自动管理连接 + 游标生命周期。
    task_function 是你传入的函数，它接收一个 cursor 参数。
    """
    conn = get_connection()
    if not conn:
        raise Exception("❌ 数据库连接失败")

    try:
        with conn.cursor() as cursor:
            result = task_function(cursor)
            conn.commit()  # 如果是写操作，确保提交
            return result
    finally:
        conn.close()
        print("✅ 数据库连接已关闭")
