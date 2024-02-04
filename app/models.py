import sqlite3
import datetime  
from flask import g

DATABASE = 'url_shortener.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

class URL:
    @staticmethod
    def find_by_original_url(original_url):
        db = get_db()
        result = db.execute('SELECT short_url FROM urls WHERE original_url = ?',
                            (original_url,)).fetchone()
        return result[0] if result else None

    @staticmethod
    def insert_short_url(original_url, short_url, expiration_date=None, max_uses=1000):
        # Calculate the expiration date if not provided
        if expiration_date is None:
            expiration_date = datetime.datetime.now() + datetime.timedelta(days=30)
        expiration_date = expiration_date.isoformat()  # Convert to string format
        
        db = get_db()
        # Insert the URL with additional fields for expiration and max uses
        db.execute('INSERT INTO urls (original_url, short_url, visit_count, expiration_date, max_uses) VALUES (?, ?, 0, ?, ?)',
                   (original_url, short_url, expiration_date, max_uses))
        db.commit()

    @staticmethod
    def get_original_url(short_url):
        db = get_db()
        result = db.execute('SELECT original_url FROM urls WHERE short_url = ?',
                            (short_url,)).fetchone()
        return result[0] if result else None

    @staticmethod
    def increment_visit_count(short_url):
        db = get_db()
        db.execute('UPDATE urls SET visit_count = visit_count + 1 WHERE short_url = ?',
                   (short_url,))
        db.commit()

    @staticmethod
    def get_visit_count(short_url):
        db = get_db()
        result = db.execute('SELECT visit_count FROM urls WHERE short_url = ?',
                            (short_url,)).fetchone()
        return result[0] if result else None

    @staticmethod
    def update_short_url(original_short_url, new_short_url):
        db = get_db()
        result = db.execute('UPDATE urls SET short_url = ? WHERE short_url = ?', (new_short_url, original_short_url))
        db.commit()
        return result.rowcount > 0

    @staticmethod
    def get_url_details(short_url):
        db = get_db()
        result = db.execute('SELECT original_url, short_url, expiration_date, max_uses FROM urls WHERE short_url = ?', (short_url,)).fetchone()
        if result:
            # Handle parsing of full ISO 8601 datetime format
            expiration_date = result[2]
            if expiration_date:
                # Adjust to parse the full datetime string
                expiration_date = datetime.datetime.strptime(expiration_date, '%Y-%m-%dT%H:%M:%S.%f').strftime('%m-%d-%Y')
            return {
                'original_url': result[0],
                'short_url': result[1],
                'expiration_date': expiration_date,  # Formatted expiration date
                'max_uses': result[3]
            }
        return None

    @staticmethod
    def update_url_details(short_url, expiration_date=None, max_uses=None):
        db = get_db()
        print(f"Updating {short_url} with expiration: {expiration_date}, max uses: {max_uses}")
        result = db.execute('UPDATE urls SET expiration_date = ?, max_uses = ? WHERE short_url = ?', 
                            (expiration_date, max_uses, short_url))
        db.commit()
        if result.rowcount > 0:
            print("Update successful")
            return True
        else:
            print("No record updated")
            return False
