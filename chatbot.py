import sqlite3
import datetime
import os
from flask import url_for

# chatbot.py
def get_response(user_message):
    # Convert the user_message to lowercase and split into individual words
    keywords = user_message.lower().split()

    # Query database for matching keyword
    with sqlite3.connect('chat_history.db') as conn:
        cursor = conn.cursor()
        # Iterate over each keyword and search in the database
        for keyword in keywords:
            cursor.execute('SELECT response, image_path FROM chatbot_responses WHERE keyword LIKE ?', ('%' + keyword + '%',))
            result = cursor.fetchone()
            
            if result:
                response, image_path = result
                if image_path:
                    # Return response with image URL
                    image_url = url_for('uploaded_file', filename=os.path.basename(image_path))
                    return [response, image_url]
                return [response]
            # Default response if no keyword match found
        return ["Maaf, saya tidak mengerti pertanyaan anda."]


import sqlite3

def get_chatbot_response(user_input):
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()

    cursor.execute("SELECT response, image_path FROM chatbot_responses WHERE keyword = ?", (user_input,))
    result = cursor.fetchone()
    conn.close()

    if result:
        response, image_path = result
        return {"response": response, "image_url": f"/uploads/{image_path}"}
    else:
        return {"response": "Sorry, I don't have that information."}


def save_message(user_id, user_message, bot_responses):
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()

    for bot_response in bot_responses:
        cursor.execute('''
            INSERT INTO chat_history (user_id, user_message, bot_response)
            VALUES (?, ?, ?)
        ''', (user_id, user_message, bot_response))

    conn.commit()
    conn.close()

def get_or_create_user(name, phone):
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM users WHERE name = ? AND phone = ?', (name, phone))
    user = cursor.fetchone()

    if user:
        user_id = user[0]
    else:
        cursor.execute('INSERT INTO users (name, phone) VALUES (?, ?)', (name, phone))
        conn.commit()
        user_id = cursor.lastrowid

    conn.close()
    return user_id

def get_frequently_asked_questions():
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT user_message, COUNT(*) as count
        FROM chat_history
        GROUP BY user_message
        ORDER BY count DESC
        LIMIT 5
    ''')
    faq_data = cursor.fetchall()
    conn.close()

    return dict(faq_data)


def get_recommended_questions(keyword):
    recommendations = []
    if "akreditas" in keyword and any(word in keyword for word in ("kampus", "stmik", "wicida")):
        recommendations = [
            "Apa akreditasi STMIK Wicida?",
            "Apa Akreditas Prodi Teknik Informatika?",
            "Apa Akreditas Prodi Sistem Informasi?",
            "Apa Akreditas Prodi Bisnis Digital?",
                                
        ]
    elif any(word in keyword for word in ("alur", "prosedur")):
        recommendations = [
            "Bagaimana alur pendaftaran jalur PMDK?",
            "Bagaimana alur pendaftaran jalur Reguler?",
            "Bagaimana alur pendaftaran jalur Alih Jenjang?",
        ]
    elif "daftar" in keyword and any(word in keyword for word in ("cara daftar", "mendaftar")):
        recommendations = [
            "Bagaimana cara mendaftar di STMIK Wicida?",
            "Prosedur pendaftaran di STMIK Wicida?",
        ]
    elif any(word in keyword for word in ("biaya", "bayar")):
        recommendations = [
            "Berapa biaya pendaftaran di STMIK Wicida?",
            "Berapa biaya daftar ulang di STMIK Wicida?",
            "Cara pembayaran biaya pendaftaran di STMIK Wicida?",
            "Bagaimana cara validasi pembayaran?",
        ]
    # Add additional logic for other relevant question recommendations here if needed
    return recommendations

