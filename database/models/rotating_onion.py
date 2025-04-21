def create_rotating_onion_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rotating_onion (
            id SERIAL PRIMARY KEY,
            address TEXT UNIQUE NOT NULL,
            private_key TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            deactivated_at TIMESTAMP NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)