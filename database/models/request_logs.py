def create_request_logs_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS request_logs (
            id SERIAL PRIMARY KEY,
            ip TEXT,
            user_agent TEXT,
            referer TEXT,
            headers JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
