def create_rotating_onion_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rotating_onion (
            id SERIAL PRIMARY KEY,
            address TEXT UNIQUE NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            deactivated_at TIMESTAMP NULL,
            expires_at TIMESTAMP NOT NULL,
            cleaned_at TIMESTAMP NULL,  -- 🆕 新增字段，标记是否已清理
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
