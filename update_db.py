import sqlite3

def update_db_schema():
    with sqlite3.connect('chat_history.db') as conn:
        cursor = conn.cursor()
        
        # Add 'image_path' column to 'chatbot_responses' table if it doesn't exist
        cursor.execute('PRAGMA table_info(chatbot_responses)')
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'image_path' not in columns:
            cursor.execute('ALTER TABLE chatbot_responses ADD COLUMN image_path TEXT')
            conn.commit()

if __name__ == '__main__':
    update_db_schema()
