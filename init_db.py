import sqlite3

def create_tables():
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()

    # Buat tabel untuk menyimpan informasi pengguna
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT
        )
    ''')

    # Buat tabel untuk menyimpan riwayat percakapan
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

    conn.commit()
    conn.close()

def reset_database():
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS chat_history')
    cursor.execute('DROP TABLE IF EXISTS users')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    reset = input("Apakah Anda ingin mereset database? (y/n): ").strip().lower()
    if reset == 'y':
        reset_database()
        print("Database telah direset.")
    create_tables()
    print("Tabel berhasil dibuat atau sudah ada.")
