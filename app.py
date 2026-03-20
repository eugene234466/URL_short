from flask import Flask, request, redirect, jsonify, render_template_string
import mysql.connector
from mysql.connector import Error
import string
import random
import os

app = Flask(__name__)

# MySQL Configuration - Railway uses MYSQLHOST, MYSQLUSER, etc.
# Check for Railway-style env vars first, then fall back to generic ones
DB_CONFIG = {
    'host': os.getenv('MYSQLHOST') or os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('MYSQLPORT') or os.getenv('DB_PORT', 3306)),
    'user': os.getenv('MYSQLUSER') or os.getenv('DB_USER', 'root'),
    'password': os.getenv('MYSQLPASSWORD') or os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('MYSQLDATABASE') or os.getenv('DB_NAME', 'url_shortener')
}

print(f"🔍 Connecting to MySQL at {DB_CONFIG['host']}:{DB_CONFIG['port']}")

# Initialize database and create table
def init_db():
    try:
        # Connect without database to create it
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.close()
        connection.close()
        
        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INT AUTO_INCREMENT PRIMARY KEY,
                short_code VARCHAR(10) UNIQUE NOT NULL,
                original_url TEXT NOT NULL,
                clicks INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_short_code (short_code)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        connection.commit()
        cursor.close()
        connection.close()
        print("✅ Database initialized successfully!")
        
    except Error as e:
        print(f"❌ Database error: {e}")

# Get database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"❌ Connection error: {e}")
        return None

# Ensure table exists before any operation
def ensure_table_exists():
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.close()
        connection.close()
        
        # Connect to the database and create table
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS urls (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    short_code VARCHAR(10) UNIQUE NOT NULL,
                    original_url TEXT NOT NULL,
                    clicks INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_short_code (short_code)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')
            connection.commit()
            cursor.close()
            connection.close()
            print("✅ Table verified/created successfully!")
    except Error as e:
        print(f"❌ Table creation error: {e}")

# Call this on app startup
ensure_table_exists()

# Generate random short code
def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(chars, k=length))
        connection = get_db_connection()
        if not connection:
            return None
            
        cursor = connection.cursor()
        cursor.execute('SELECT short_code FROM urls WHERE short_code = %s', (code,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return code
        cursor.close()
        connection.close()

# Modern HTML template (same as before)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#667eea">
    <meta name="description" content="Simple and fast URL shortener">
    <title>🔗 URL Shortener</title>
    <link rel="manifest" href="/manifest.json">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        #container {
            max-width: 500px;
            width: 100%;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            animation: slideUp 0.6s ease;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        h1 {
            font-size: 32px;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 8px;
            text-align: center;
        }
        
        .subtitle {
            text-align: center;
            color: #6b7280;
            font-size: 14px;
            margin-bottom: 32px;
        }
        
        input[type="text"] { 
            width: 100%; 
            padding: 16px 20px;
            margin: 10px 0;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: #f9fafb;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
            background: white;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        }
        
        input[type="text"]::placeholder {
            color: #9ca3af;
        }
        
        button { 
            width: 100%;
            padding: 16px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            margin-top: 8px;
        }
        
        button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .result { 
            margin-top: 24px;
            padding: 20px;
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-radius: 16px;
            border-left: 4px solid #28a745;
            animation: fadeIn 0.5s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .result strong {
            display: block;
            color: #155724;
            font-size: 14px;
            margin-bottom: 12px;
            font-weight: 600;
        }
        
        .result a {
            display: inline-block;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            padding: 12px 16px;
            background: white;
            border-radius: 8px;
            margin-top: 8px;
            transition: all 0.2s ease;
        }
        
        .result a:hover {
            background: #f3f4f6;
            transform: translateX(4px);
        }
        
        .error { 
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            border-left: 4px solid #dc3545;
        }
        
        .error strong {
            color: #721c24;
        }
        
        .icon {
            font-size: 48px;
            text-align: center;
            margin-bottom: 16px;
        }
        
        .footer {
            text-align: center;
            margin-top: 24px;
            color: white;
            font-size: 13px;
            opacity: 0.9;
        }
        
        .db-badge {
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            margin-left: 8px;
        }
        
        @media (max-width: 600px) {
            .card {
                padding: 28px 24px;
            }
            
            h1 {
                font-size: 28px;
            }
        }
    </style>
</head>
<body>
    <div id="container">
        <div class="card">
            <div class="icon">🔗</div>
            <h1>URL Shortener <span class="db-badge">MySQL</span></h1>
            <p class="subtitle">Fast, simple, works offline</p>
            
            <form id="urlForm">
                <input type="text" id="urlInput" placeholder="Enter your long URL here..." required>
                <button type="submit">✨ Shorten URL</button>
            </form>
            <div id="result"></div>
        </div>
        
        <div class="footer">
            Built with 💜 • MySQL Database • Production Ready
        </div>
    </div>
    
    <script>
        document.getElementById('urlForm').onsubmit = async (e) => {
            e.preventDefault();
            const url = document.getElementById('urlInput').value;
            const response = await fetch('/shorten', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: url})
            });
            const data = await response.json();
            const resultDiv = document.getElementById('result');
            if (data.short_url) {
                resultDiv.className = 'result';
                resultDiv.innerHTML = `<strong>✅ Your shortened URL:</strong><br>
                    <a href="${data.short_url}" target="_blank">${data.short_url}</a>`;
            } else {
                resultDiv.className = 'result error';
                resultDiv.innerHTML = `<strong>❌ Error:</strong> ${data.error}`;
            }
        };
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "URL Shortener",
        "short_name": "ShortURL",
        "description": "Fast and simple URL shortener with MySQL",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#667eea",
        "orientation": "portrait",
        "icons": [
            {
                "src": "/static/icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/static/icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    })

@app.route('/shorten', methods=['POST'])
def shorten_url():
    try:
        data = request.get_json()
        original_url = data.get('url', '').strip()
        
        if not original_url:
            return jsonify({'error': 'URL is required'}), 400
        
        if not original_url.startswith(('http://', 'https://')):
            original_url = 'https://' + original_url
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Check if URL already exists
        cursor.execute('SELECT short_code FROM urls WHERE original_url = %s', (original_url,))
        existing = cursor.fetchone()
        
        if existing:
            short_code = existing['short_code']
        else:
            short_code = generate_short_code()
            if not short_code:
                cursor.close()
                connection.close()
                return jsonify({'error': 'Failed to generate short code'}), 500
            
            cursor.execute(
                'INSERT INTO urls (short_code, original_url) VALUES (%s, %s)',
                (short_code, original_url)
            )
            connection.commit()
        
        cursor.close()
        connection.close()
        
        short_url = request.host_url + short_code
        return jsonify({'short_url': short_url, 'short_code': short_code})
        
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/<short_code>')
def redirect_url(short_code):
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT original_url FROM urls WHERE short_code = %s', (short_code,))
        result = cursor.fetchone()
        
        if result:
            # Increment click counter
            cursor.execute('UPDATE urls SET clicks = clicks + 1 WHERE short_code = %s', (short_code,))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(result['original_url'])
        
        cursor.close()
        connection.close()
        return jsonify({'error': 'URL not found'}), 404
        
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500

@app.route('/stats/<short_code>')
def stats(short_code):
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            'SELECT original_url, clicks, created_at FROM urls WHERE short_code = %s',
            (short_code,)
        )
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if result:
            return jsonify({
                'short_code': short_code,
                'original_url': result['original_url'],
                'clicks': result['clicks'],
                'created_at': str(result['created_at'])
            })
        return jsonify({'error': 'URL not found'}), 404
        
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500

if __name__ == '__main__':
    print("🚀 Initializing URL Shortener with MySQL...")
    init_db()
    print("✅ Server starting on http://localhost:5000")
    app.run(debug=True, port=5000)
