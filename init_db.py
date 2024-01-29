import sqlite3

def create_table():
    conn = sqlite3.connect('url_shortener.db')
    cursor = conn.cursor()

    # Create the urls table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_url TEXT NOT NULL,
            visit_count INTEGER DEFAULT 0
        )
    ''')

    # Add visit_count column if it doesn't exist
    cursor.execute('''
        PRAGMA table_info(urls)
    ''')
    columns = [row[1] for row in cursor.fetchall()]
    if 'visit_count' not in columns:
        cursor.execute('''
            ALTER TABLE urls
            ADD COLUMN visit_count INTEGER DEFAULT 0
        ''')

    # Add expiration_date column if it doesn't exist
    if 'expiration_date' not in columns:
        cursor.execute('''
            ALTER TABLE urls
            ADD COLUMN expiration_date DATETIME
        ''')

    # Add max_uses column if it doesn't exist
    if 'max_uses' not in columns:
        cursor.execute('''
            ALTER TABLE urls
            ADD COLUMN max_uses INTEGER
        ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_table()
    print("Database and table created or updated successfully.")
