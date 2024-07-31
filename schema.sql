-- schema.sql

-- Tabel untuk menyimpan informasi pengguna
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL
);

-- Tabel untuk menyimpan histori percakapan
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS keyword_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    response TEXT NOT NULL,
    image_url TEXT
);

import sqlite3

with sqlite3.connect('chat_history.db') as conn:
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(chat_history);')
    print(cursor.fetchall())

cursor.execute('PRAGMA table_info(chatbot_responses);')
print(cursor.fetchall())
