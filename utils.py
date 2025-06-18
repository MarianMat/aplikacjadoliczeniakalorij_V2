import sqlite3
import bcrypt
from datetime import datetime

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL,
            email TEXT,
            first_use TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password, email=None):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            'INSERT INTO users (username, password_hash, email, first_use) VALUES (?, ?, ?, ?)',
            (username, password_hash, email, None)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return False  # użytkownik już istnieje
    conn.close()
    return True

def verify_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    if row:
        stored_hash = row[0]
        return bcrypt.checkpw(password.encode(), stored_hash)
    return False

def update_first_use(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT first_use FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    if not row or row[0] is None:
        now = datetime.now().isoformat()
        c.execute('UPDATE users SET first_use = ? WHERE username = ?', (now, username))
        conn.commit()
    conn.close()

def get_first_use(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT first_use FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None
