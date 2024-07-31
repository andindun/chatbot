from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
import sqlite3
from datetime import datetime
import pytz
import re
import os
from werkzeug.utils import secure_filename
from chatbot import get_response, get_or_create_user


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Example login check (replace with your actual authentication logic)
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return 'Login failed. Please check your username and password.'
    return render_template('login.html')

@app.route('/admin')
def admin_dashboard():
    if 'logged_in' in session and session['logged_in']:
        with sqlite3.connect('chat_history.db') as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT u.name, u.phone, ch.user_message, ch.bot_response, ch.timestamp, ch.id
                FROM chat_history ch
                JOIN users u ON ch.user_id = u.id
                ORDER BY ch.timestamp DESC
            ''')
            chat_history = cursor.fetchall()

            cursor.execute('SELECT id, keyword, response, image_path FROM chatbot_responses')
            responses = cursor.fetchall()

        chat_history_wita = [
            (name, phone, user_message, bot_response, convert_to_wita(timestamp), id)
            for name, phone, user_message, bot_response, timestamp, id in chat_history
        ]

        return render_template('admin.html', chat_history=chat_history_wita, responses=responses)
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

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

        # Table to store keyword responses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chatbot_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT,
                response TEXT,
                image_url TEXT
            )
        ''')


# Function to convert time to WITA (Central Indonesia Time)
def convert_to_wita(timestamp_utc):
    tz_wita = pytz.timezone('Asia/Makassar')  # WITA (Waktu Indonesia Tengah)
    tz_utc = pytz.timezone('UTC')

    # Parse timestamp from string format to datetime object
    timestamp_utc = datetime.strptime(timestamp_utc, '%Y-%m-%d %H:%M:%S')
    timestamp_utc = tz_utc.localize(timestamp_utc)  # Add UTC timezone info
    timestamp_wita = timestamp_utc.astimezone(tz_wita)  # Convert to WITA timezone

    return timestamp_wita.strftime('%Y-%m-%d %H:%M:%S %Z')  # Format time to WITA

# Function to get recommended questions based on keywords
def get_recommended_questions(keyword):
    # Default recommendations
    default_recommendations = [
        "Akreditas Kampus",
        "Program Studi",
        "Cara Daftar",
        "Cara Pembayaran",
        "Validasi"
    ]

    # List to store dynamic recommendations
    recommendations = []

    # Check for additional recommendations based on keyword
    if "akreditas" in keyword and any(word in keyword for word in ("kampus", "stmik", "wicida")):
        recommendations.extend([
            "Apa akreditas STMIK Wicida?",
            "Apa Akreditas Prodi Teknik Informatika?",
            "Apa Akreditas Prodi Sistem Informasi?",
            "Apa Akreditas Prodi Bisnis Digital?",
        ])
    elif any(word in keyword for word in ("alur", "prosedur")):
        recommendations.extend([
            "Apa saja persyaratan pendaftaran jalur PMDK?",
            "Apa saja persyaratan pendaftaran jalur Reguler?",
            "Apa saja persyaratan pendaftaran jalur Alih Jenjang?",
        ])
    elif "daftar" in keyword and any(word in keyword for word in ("cara daftar", "mendaftar")):
        recommendations.extend([
            "Bagaimana cara mendaftar di STMIK Wicida?",
            "Prosedur pendaftaran di STMIK Wicida?",
        ])
    elif any(word in keyword for word in ("biaya", "bayar", "cara bayar")):
        recommendations.extend([
            "Berapa biaya pendaftaran di STMIK Wicida?",
            "Berapa biaya daftar ulang di STMIK Wicida?",
            "Cara pembayaran biaya pendaftaran di STMIK Wicida?",
            "Bagaimana cara validasi pembayaran?",
        ])
    else:
        recommendations = default_recommendations

    return recommendations

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to initialize session
@app.route('/init_session', methods=['POST'])
def init_session():
    session.clear()
    return jsonify("Halo! Selamat datang!" + "\nSebelum bertanya, tolong sebutkan nama anda.")

# Function to validate name
def validate_name(name):
    return re.match(r'^[a-zA-Z\s]+$', name)

# Function to validate phone number (Indonesia format)
def validate_phone(phone):
    return re.match(r'^[0-9]{10,12}$', phone)

# Route to get response from chatbot
@app.route('/get_response', methods=['POST'])
def get_bot_response():
    user_message = request.json['message']
    user_info = session.get('user_info', {})

    if 'name' not in user_info:
        if not validate_name(user_message):
            return jsonify({'responses': ["Nama hanya boleh mengandung huruf dan spasi. Silakan masukkan nama anda kembali."]})

        user_info['name'] = user_message
        session['user_info'] = user_info
        return jsonify({'responses': ["Tolong berikan nomor telepon anda juga ya."]})

    if 'phone' not in user_info:
        if not validate_phone(user_message):
            return jsonify({'responses': ["Nomor telepon harus terdiri dari 10-12 digit angka. Silakan masukkan nomor telepon anda kembali."]})

        user_info['phone'] = user_message
        session['user_info'] = user_info

        user_id = get_or_create_user(user_info['name'], user_info['phone'])
        session['user_id'] = user_id

        return jsonify({
            'responses': [f"Terima kasih, {user_info['name']}! Apa ada yang ingin ditanyakan?"],
            'recommendations': get_recommended_questions(user_message.lower())
        })

    user_id = session.get('user_id')
    bot_responses = get_response(user_message)  # Assumed to return a list of responses

    # Logic to add recommendations based on keywords
    recommendations = get_recommended_questions(user_message.lower())

    save_message(user_id, user_message, bot_responses)

    return jsonify({
        'responses': bot_responses,
        'recommendations': recommendations
    })

# Function to save message to database
def save_message(user_id, user_message, bot_response):
    with sqlite3.connect('chat_history.db') as conn:
        cursor = conn.cursor()

        combined_bot_response = ' '.join(bot_response)

        cursor.execute('''
            INSERT INTO chat_history (user_id, user_message, bot_response)
            VALUES (?, ?, ?)
        ''', (user_id, user_message, combined_bot_response))
        conn.commit()

# Route to get frequently asked questions data
@app.route('/faq_data')
def get_faq_data():
    with sqlite3.connect('chat_history.db') as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT user_message, COUNT(*) AS count
            FROM chat_history
            GROUP BY user_message
            ORDER BY count DESC
            LIMIT 5
        ''')

        faq_data = cursor.fetchall()
        return jsonify(faq_data)

# Route to get weekly question counts
@app.route('/weekly_question_counts')
def get_weekly_question_counts():
    with sqlite3.connect('chat_history.db') as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT STRFTIME('%Y-%m-%d', timestamp) AS time_period, COUNT(*) AS count
            FROM chat_history
            WHERE timestamp >= DATETIME('now', '-7 days')
            GROUP BY time_period
        ''')

        weekly_counts = cursor.fetchall()
        return jsonify(weekly_counts)

# Route to get monthly question counts
@app.route('/monthly_question_counts')
def get_monthly_question_counts():
    with sqlite3.connect('chat_history.db') as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT STRFTIME('%Y-%m', timestamp) AS time_period, COUNT(*) AS count
            FROM chat_history
            WHERE timestamp >= DATETIME('now', '-1 month')
            GROUP BY time_period
        ''')

        monthly_counts = cursor.fetchall()
        return jsonify(monthly_counts)

@app.route('/manage_responses', methods=['POST'])
def manage_responses():
    if 'logged_in' in session and session['logged_in']:
        keywords = request.form.get('keywords').split(',')
        response = request.form.get('response')
        image = request.files.get('image')
        image_path = None

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

        with sqlite3.connect('chat_history.db') as conn:
            cursor = conn.cursor()
            for keyword in keywords:
                keyword = keyword.strip()
                if keyword:
                    cursor.execute('INSERT INTO chatbot_responses (keyword, response, image_path) VALUES (?, ?, ?)', 
                                   (keyword, response, image_path))
            conn.commit()
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('login'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Route to delete all messages from database
@app.route('/delete_all_messages', methods=['POST'])
def delete_all_messages():
    with sqlite3.connect('chat_history.db') as conn:
        cursor = conn.cursor()

        cursor.execute('DELETE FROM chat_history')
        conn.commit()

    return redirect('/admin')

# Route to delete message by ID
@app.route('/delete_message/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    with sqlite3.connect('chat_history.db') as conn:
        cursor = conn.cursor()

        cursor.execute('DELETE FROM chat_history WHERE id = ?', (message_id,))
        conn.commit()

    return redirect('/admin')
@app.route('/delete_response/<int:id>', methods=['POST'])
def delete_response(id):
    if 'logged_in' in session and session['logged_in']:
        with sqlite3.connect('chat_history.db') as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM chatbot_responses WHERE id = ?', (id,))
            conn.commit()
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('login'))
    
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
    update_db_schema()  # Ensure the database schema is up to date
    app.run(debug=True)

