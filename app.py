from flask import Flask, request, redirect, jsonify, render_template_string, send_from_directory
import sqlite3
import string
import random
import os

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

# PWA-Enhanced HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#007bff">
    <meta name="description" content="Simple and fast URL shortener">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>URL Shortener</title>
    <link rel="manifest" href="/manifest.json">
    <link rel="icon" type="image/png" href="/static/icon-192.png">
    <link rel="apple-touch-icon" href="/static/icon-192.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 30px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { 
            color: #333; 
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        input[type="text"] { 
            width: 100%; 
            padding: 15px; 
            margin: 10px 0;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        button { 
            width: 100%;
            padding: 15px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s;
        }
        button:hover { 
            transform: translateY(-2px);
        }
        button:active {
            transform: translateY(0);
        }
        .result { 
            margin-top: 20px; 
            padding: 20px; 
            background: #e8f5e9;
            border-radius: 10px;
            border-left: 4px solid #4caf50;
        }
        .error { 
            background: #ffebee;
            border-left-color: #f44336;
        }
        .result strong {
            display: block;
            margin-bottom: 10px;
            color: #333;
        }
        .short-url {
            background: white;
            padding: 12px;
            border-radius: 8px;
            word-break: break-all;
            font-family: monospace;
            font-size: 14px;
            margin-top: 8px;
        }
        .short-url a {
            color: #667eea;
            text-decoration: none;
        }
        .copy-btn {
            margin-top: 10px;
            width: auto;
            padding: 8px 20px;
            background: #4caf50;
            font-size: 14px;
        }
        .install-prompt {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
        }
        .install-prompt button {
            margin-top: 10px;
            background: #ffc107;
            color: #000;
        }
        .offline-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #f44336;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            display: none;
            font-size: 14px;
        }
        .online {
            background: #4caf50;
        }
    </style>
</head>
<body>
    <div class="offline-indicator" id="offlineIndicator">Offline</div>
    
    <div class="container">
        <div class="install-prompt" id="installPrompt">
            <strong>📱 Install this app!</strong>
            <p style="margin-top: 8px; font-size: 14px;">Add to your home screen for quick access</p>
            <button id="installBtn">Install Now</button>
        </div>
        
        <h1>🔗 URL Shortener</h1>
        <p class="subtitle">Fast, simple, works offline</p>
        
        <form id="urlForm">
            <input type="text" id="urlInput" placeholder="Enter long URL" required>
            <button type="submit">Shorten URL</button>
        </form>
        <div id="result"></div>
    </div>
    
    <script>
        // Service Worker Registration
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(reg => console.log('Service Worker registered'))
                .catch(err => console.log('Service Worker error:', err));
        }
        
        // Install prompt
        let deferredPrompt;
        const installPrompt = document.getElementById('installPrompt');
        const installBtn = document.getElementById('installBtn');
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            installPrompt.style.display = 'block';
        });
        
        installBtn.addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                if (outcome === 'accepted') {
                    installPrompt.style.display = 'none';
                }
                deferredPrompt = null;
            }
        });
        
        // Online/Offline indicator
        const offlineIndicator = document.getElementById('offlineIndicator');
        
        window.addEventListener('online', () => {
            offlineIndicator.textContent = 'Back Online';
            offlineIndicator.classList.add('online');
            offlineIndicator.style.display = 'block';
            setTimeout(() => offlineIndicator.style.display = 'none', 3000);
        });
        
        window.addEventListener('offline', () => {
            offlineIndicator.textContent = 'Offline Mode';
            offlineIndicator.classList.remove('online');
            offlineIndicator.style.display = 'block';
        });
        
        // Form submission
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
                resultDiv.innerHTML = `
                    <strong>✅ Shortened URL:</strong>
                    <div class="short-url">
                        <a href="${data.short_url}" target="_blank">${data.short_url}</a>
                    </div>
                    <button class="copy-btn" onclick="copyToClipboard('${data.short_url}')">
                        📋 Copy Link
                    </button>
                `;
            } else {
                resultDiv.className = 'result error';
                resultDiv.innerHTML = `<strong>❌ Error:</strong> ${data.error}`;
            }
        };
        
        // Copy to clipboard
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = '✓ Copied!';
                setTimeout(() => btn.textContent = originalText, 2000);
            });
        }
        
        // Share API (if available)
        async function shareUrl(url) {
            if (navigator.share) {
                try {
                    await navigator.share({
                        title: 'Shortened URL',
                        text: 'Check out this link:',
                        url: url
                    });
                } catch (err) {
                    console.log('Share failed:', err);
                }
            }
        }
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
        "description": "Fast and simple URL shortener",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#007bff",
        "orientation": "portrait",
        "icons": [
            {
                "src": "/static/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "/static/icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ]
    })

@app.route('/sw.js')
def service_worker():
    sw_code = '''
const CACHE_NAME = 'url-shortener-v1';
const urlsToCache = [
  '/',
  '/manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
      .catch(() => caches.match('/'))
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(name => name !== CACHE_NAME)
          .map(name => caches.delete(name))
      );
    })
  );
});
'''
    return sw_code, 200, {'Content-Type': 'application/javascript'}

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    original_url = data.get('url', '').strip()
    
    if not original_url:
        return jsonify({'error': 'URL is required'}), 400
    
    if not original_url.startswith(('http://', 'https://')):
        original_url = 'https://' + original_url
    
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
        c.execute('UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?', (short_code,))
        conn.commit()
        conn.close()
        return redirect(result[0])
    
    conn.close()
    return jsonify({'error': 'URL not found'}), 404

if __name__ == '__main__':
    # Create static folder for icons
    os.makedirs('static', exist_ok=True)
    init_db()
    
    print("\n🚀 PWA URL Shortener starting...")
    print("📱 Visit http://localhost:5000 and install it as an app!\n")
    
    app.run(debug=True, port=5000)
