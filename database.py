import sqlite3
from datetime import datetime
import logging
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)

DATABASE_PATH = 'exchange_bot.db'

@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize database tables."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Queue table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS queue (
                queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                user_name TEXT NOT NULL,
                status TEXT DEFAULT 'waiting',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                notes TEXT
            )
        ''')
        
        # Alert subscriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                user_name TEXT,
                target_rate REAL NOT NULL,
                condition TEXT DEFAULT 'above',
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                triggered_at TIMESTAMP
            )
        ''')
        
        # Rate history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                buying_tt REAL,
                selling_tt REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Admin users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                user_name TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        logging.info("Database initialized successfully")

def save_rate_history(rates):
    """Save rate data to history."""
    with get_db() as conn:
        cursor = conn.cursor()
        for rate in rates:
            if rate.get('status') in ['success', 'fallback']:
                cursor.execute('''
                    INSERT INTO rate_history (provider, buying_tt, selling_tt, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (
                    rate['provider'],
                    rate.get('buying_tt'),
                    rate.get('selling_tt'),
                    datetime.now()
                ))
        conn.commit()

def get_latest_rates():
    """Get the most recent rates for each provider."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT provider, buying_tt, selling_tt, MAX(timestamp) as timestamp
            FROM rate_history
            GROUP BY provider
            ORDER BY buying_tt DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]

def is_admin(user_id):
    """Check if user is an admin."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE user_id = ?', (user_id,))
        return cursor.fetchone() is not None

def add_admin(user_id, user_name=None):
    """Add a user as admin."""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO admins (user_id, user_name) VALUES (?, ?)', 
                         (user_id, user_name))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")
