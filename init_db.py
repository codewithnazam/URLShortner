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

    # Optionally, check if the visit_count column exists and add it if it doesn't
    cursor.execute('''
        PRAGMA table_info(urls)
    ''')
    columns = [row[1] for row in cursor.fetchall()]
    if 'visit_count' not in columns:
        cursor.execute('''
            ALTER TABLE urls
            ADD COLUMN visit_count INTEGER DEFAULT 0
        ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_table()
    print("Database and table created or updated successfully.")
