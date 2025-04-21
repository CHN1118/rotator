import psycopg2
from database.config import DB_CONFIG

def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        return conn
    except Exception as e:
        print("❌ 数据库连接失败：", e)
        return None

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
