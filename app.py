from flask import Flask, request, redirect, jsonify, render_template_string
import sqlite3
import string
import random
import os

app = Flask(__name__)
DB_NAME = 'urls.db'

# ---------- DATABASE ----------

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE NOT NULL,
            original_url TEXT NOT NULL,
            clicks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# 🔥 IMPORTANT: Run on startup (works on Render)
init_db()


# ---------- UTIL ----------

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(chars, k=length))

        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT short_code FROM urls WHERE short_code = ?', (code,))
        exists = c.fetchone()
        conn.close()

        if not exists:
            return code


# ---------- FRONTEND ----------

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<title>URL Shortener</title>
</head>
<body style="font-family:sans-serif; text-align:center; padding:50px;">
<h1>🔗 URL Shortener</h1>
<form id="form">
<input type="text" id="url" placeholder="Enter URL" style="width:300px; padding:10px;" required>
<br><br>
<button type="submit">Shorten</button>
</form>
<div id="result"></div>

<script>
document.getElementById("form").onsubmit = async (e) => {
    e.preventDefault();

    const url = document.getElementById("url").value;

    const res = await fetch("/shorten", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({url})
    });

    const data = await res.json();

    if (data.short_url) {
        document.getElementById("result").innerHTML =
            "<p><b>Short URL:</b> <a href='" + data.short_url + "'>" + data.short_url + "</a></p>";
    } else {
        document.getElementById("result").innerText = data.error;
    }
};
</script>
</body>
</html>
"""


# ---------- ROUTES ----------

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

    conn = get_db()
    c = conn.cursor()

    # Check existing
    c.execute('SELECT short_code FROM urls WHERE original_url = ?', (original_url,))
    existing = c.fetchone()

    if existing:
        short_code = existing['short_code']
    else:
        short_code = generate_short_code()
        c.execute(
            'INSERT INTO urls (short_code, original_url) VALUES (?, ?)',
            (short_code, original_url)
        )
        conn.commit()

    conn.close()

    short_url = request.host_url + short_code
    return jsonify({'short_url': short_url})


@app.route('/<short_code>')
def redirect_url(short_code):
    conn = get_db()
    c = conn.cursor()

    c.execute('SELECT original_url FROM urls WHERE short_code = ?', (short_code,))
    result = c.fetchone()

    if result:
        c.execute(
            'UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?',
            (short_code,)
        )
        conn.commit()
        conn.close()
        return redirect(result['original_url'])

    conn.close()
    return jsonify({'error': 'URL not found'}), 404


# ---------- LOCAL RUN ----------

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    print("🚀 Running locally...")
    app.run(debug=True)