from flask import Flask, request, redirect, jsonify, render_template_string
import sqlite3
import string
import random

app = Flask(__name__)
DB_NAME = 'urls.db'

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  short_code TEXT UNIQUE NOT NULL,
                  original_url TEXT NOT NULL,
                  clicks INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Generate random short code
def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(chars, k=length))
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT short_code FROM urls WHERE short_code = ?', (code,))
        if not c.fetchone():
            conn.close()
            return code
        conn.close()

# Simple HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>URL Shortener</title>
    <style>
        body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }
        input[type="text"] { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin-top: 20px; padding: 15px; background: #d4edda; border-radius: 5px; }
        .error { background: #f8d7da; }
    </style>
</head>
<body>
    <h1>🔗 URL Shortener</h1>
    <form id="urlForm">
        <input type="text" id="urlInput" placeholder="Enter long URL" required>
        <button type="submit">Shorten URL</button>
    </form>
    <div id="result"></div>
    
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
                resultDiv.innerHTML = `<strong>Shortened URL:</strong><br>
                    <a href="${data.short_url}" target="_blank">${data.short_url}</a>`;
            } else {
                resultDiv.className = 'result error';
                resultDiv.innerHTML = `<strong>Error:</strong> ${data.error}`;
            }
        };
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    original_url = data.get('url', '').strip()
    
    if not original_url:
        return jsonify({'error': 'URL is required'}), 400
    
    if not original_url.startswith(('http://', 'https://')):
        original_url = 'https://' + original_url
    
    # Check if URL already exists
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT short_code FROM urls WHERE original_url = ?', (original_url,))
    existing = c.fetchone()
    
    if existing:
        short_code = existing[0]
    else:
        short_code = generate_short_code()
        c.execute('INSERT INTO urls (short_code, original_url) VALUES (?, ?)',
                  (short_code, original_url))
        conn.commit()
    
    conn.close()
    
    short_url = request.host_url + short_code
    return jsonify({'short_url': short_url, 'short_code': short_code})

@app.route('/<short_code>')
def redirect_url(short_code):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT original_url FROM urls WHERE short_code = ?', (short_code,))
    result = c.fetchone()
    
    if result:
        # Increment click counter
        c.execute('UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?', (short_code,))
        conn.commit()
        conn.close()
        return redirect(result[0])
    
    conn.close()
    return jsonify({'error': 'URL not found'}), 404

@app.route('/stats/<short_code>')
def stats(short_code):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT original_url, clicks, created_at FROM urls WHERE short_code = ?', (short_code,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return jsonify({
            'short_code': short_code,
            'original_url': result[0],
            'clicks': result[1],
            'created_at': result[2]
        })
    return jsonify({'error': 'URL not found'}), 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)