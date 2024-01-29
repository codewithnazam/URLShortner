import sqlite3
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
    def insert_short_url(original_url, short_url):
        db = get_db()
        db.execute('INSERT INTO urls (original_url, short_url) VALUES (?, ?)',
                   (original_url, short_url))
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
    def insert_short_url(original_url, short_url, expiration_date=None, max_uses=1000):
        if expiration_date is None:
            expiration_date = datetime.datetime.now() + datetime.timedelta(days=30)
        expiration_date = expiration_date.isoformat()  # Convert to a string format

        db = get_db()
        db.execute('INSERT INTO urls (original_url, short_url, visit_count, expiration_date, max_uses) VALUES (?, ?, 0, ?, ?)',
                   (original_url, short_url, expiration_date, max_uses))
        db.commit()