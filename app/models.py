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
