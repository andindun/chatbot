# models.py
import sqlite3

def init_db():
    with sqlite3.connect('chat_history.db') as conn:
        cursor = conn.cursor()

        # Table to store chat history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_message TEXT,
                bot_response TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Table to store user information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT
            )
        ''')

        # Table to store chatbot keywords and responses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chatbot_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT,
                response TEXT
            )
        ''')
