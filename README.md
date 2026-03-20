# 🔗 URL Shortener - Progressive Web App

A simple, fast, and beautiful URL shortener built with Python Flask. Works offline, installable as a mobile app, and requires no signup!

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)
![PWA](https://img.shields.io/badge/PWA-enabled-purple.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- 🚀 **Fast & Simple** - Shorten URLs in seconds
- 📱 **Progressive Web App** - Install on any device
- 🌐 **Works Offline** - Service Worker caching
- 📊 **Click Tracking** - See how many times your links are clicked
- 📋 **One-Click Copy** - Copy shortened URLs instantly
- 💾 **Persistent Storage** - SQLite database
- 🎨 **Beautiful UI** - Modern gradient design
- 🔒 **No Signup Required** - Start shortening immediately

## 📸 Screenshots

```
┌─────────────────────────────┐
│  🔗 URL Shortener          │
│  Fast, simple, works offline│
├─────────────────────────────┤
│  Enter long URL:            │
│  ┌─────────────────────┐   │
│  │ https://example...  │   │
│  └─────────────────────┘   │
│        [Shorten URL]        │
├─────────────────────────────┤
│  ✅ Shortened URL:          │
│  http://localhost/aB3xYz    │
│       [📋 Copy Link]        │
└─────────────────────────────┘
```

## 🛠️ Tech Stack

**Backend:**
- Python 3.8+
- Flask 2.0+
- SQLite3

**Frontend:**
- HTML5
- CSS3
- Vanilla JavaScript
- Service Workers (PWA)

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/url-shortener-pwa.git
cd url-shortener-pwa
```

2. **Install dependencies**
```bash
pip install flask
```

3. **Run the application**
```bash
python app.py
```

4. **Open in browser**
```
http://localhost:5000
```

That's it! 🎉

## 📁 Project Structure

```
url-shortener-pwa/
├── app.py              # Main Flask application
├── urls.db            # SQLite database (auto-created)
├── static/            # Static assets
│   ├── icon-192.png   # PWA icon 192x192
│   └── icon-512.png   # PWA icon 512x512
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## 🚀 Usage

### Shorten a URL

1. Enter your long URL in the input field
2. Click "Shorten URL"
3. Copy the generated short link
4. Share it anywhere!

### Access Shortened URL

Visit: `http://your-domain.com/shortcode`

Example: `http://localhost:5000/aB3xYz`

### View Statistics

Visit: `http://your-domain.com/stats/shortcode`

Example: `http://localhost:5000/stats/aB3xYz`

Returns:
```json
{
  "short_code": "aB3xYz",
  "original_url": "https://example.com/very/long/url",
  "clicks": 42,
  "created_at": "2025-02-11 10:30:00"
}
```

## 📱 PWA Installation

### Android (Chrome)
1. Visit the URL shortener
2. Tap the "Add to Home Screen" prompt
3. Or tap menu (⋮) → "Install app"
4. App icon appears on home screen!

### iOS (Safari)
1. Visit the URL shortener
2. Tap Share button (⬆️)
3. Select "Add to Home Screen"
4. Tap "Add"

### Desktop (Chrome/Edge)
1. Visit the URL shortener
2. Click install icon in address bar
3. Or click menu (⋮) → "Install URL Shortener"
4. App opens in its own window!

## 🌐 Deployment

### Option 1: Render (Free)

1. Create `requirements.txt`:
```
flask==2.3.0
gunicorn==21.2.0
```

2. Create `render.yaml`:
```yaml
services:
  - type: web
    name: url-shortener
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
```

3. Push to GitHub
4. Connect to Render
5. Deploy! 🚀

**Live in 5 minutes!**

### Option 2: Railway

1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Login and deploy:
```bash
railway login
railway init
railway up
```

3. Get your URL:
```bash
railway domain
```

**Live in 2 minutes!** ⚡

### Option 3: PythonAnywhere

1. Upload files to PythonAnywhere
2. Create web app (Flask)
3. Point to `app.py`
4. Reload app
5. Done!

### Option 4: Heroku

1. Create `Procfile`:
```
web: gunicorn app:app
```

2. Create `runtime.txt`:
```
python-3.11.0
```

3. Deploy:
```bash
heroku create your-shortener
git push heroku main
```

### Option 5: Self-Hosted (VPS)

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip nginx

# Clone and setup
git clone https://github.com/yourusername/url-shortener.git
cd url-shortener
pip3 install -r requirements.txt

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Setup nginx as reverse proxy
# Configure domain and SSL
```

## 🔧 Configuration

### Change Port

```python
# app.py - last line
app.run(debug=True, port=8000)  # Change from 5000 to 8000
```

### Change Short Code Length

```python
# app.py - Line ~28
def generate_short_code(length=6):  # Change from 6 to any number
```

### Custom Domain

After deployment, update `manifest.json`:

```python
# app.py - manifest route
"start_url": "https://yourdomain.com/",
```

## 🎨 Customization

### Change Colors

Edit the gradient in the HTML template (around line 50):

```python
HTML_TEMPLATE = '''
<style>
    body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        /* Change to your colors! */
    }
</style>
'''
```

### Add Custom Icon

Replace files in `static/` folder:
- `icon-192.png` (192x192 pixels)
- `icon-512.png` (512x512 pixels)

Generate icons: [Favicon.io](https://favicon.io/)

## 📊 Database Schema

```sql
CREATE TABLE urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_code TEXT UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    clicks INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Example Queries

**Get all URLs:**
```sql
SELECT * FROM urls ORDER BY created_at DESC;
```

**Get popular URLs:**
```sql
SELECT * FROM urls ORDER BY clicks DESC LIMIT 10;
```

**Delete old URLs:**
```sql
DELETE FROM urls WHERE created_at < date('now', '-30 days');
```

## 🔒 Security Considerations

### Production Checklist

- [ ] Use environment variables for secrets
- [ ] Enable HTTPS (required for PWA)
- [ ] Add rate limiting
- [ ] Validate URLs properly
- [ ] Sanitize database inputs
- [ ] Add CORS headers if needed
- [ ] Implement URL expiration
- [ ] Add abuse prevention

### Rate Limiting (Recommended)

```python
from flask_limiter import Limiter

limiter = Limiter(app, default_limits=["100 per hour"])

@app.route('/shorten', methods=['POST'])
@limiter.limit("10 per minute")
def shorten_url():
    # Your code here
```

Install: `pip install Flask-Limiter`

## 🧪 Testing

### Manual Testing

1. **Shorten URL:**
   - Enter: `https://www.google.com`
   - Verify short code generated
   - Verify URL saved in database

2. **Redirect:**
   - Visit: `http://localhost:5000/[shortcode]`
   - Verify redirects to original URL
   - Check clicks incremented

3. **Stats:**
   - Visit: `http://localhost:5000/stats/[shortcode]`
   - Verify JSON response

4. **Offline Mode:**
   - Open DevTools → Network
   - Check "Offline"
   - Refresh page
   - App should still load!

5. **PWA Install:**
   - Check for install prompt
   - Install app
   - Verify works as standalone app

### Automated Testing (Optional)

```python
# test_app.py
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    rv = client.get('/')
    assert rv.status_code == 200

def test_shorten_url(client):
    rv = client.post('/shorten', 
        json={'url': 'https://example.com'})
    assert rv.status_code == 200
    assert 'short_url' in rv.json
```

Run: `pytest test_app.py`

## 📈 Analytics (Optional)

Track usage with Google Analytics:

```python
# Add to HTML template
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

## 🐛 Troubleshooting

### Database Error
```
Error: unable to open database file
```
**Solution:** Ensure write permissions in directory
```bash
chmod 755 .
```

### Module Not Found
```
ModuleNotFoundError: No module named 'flask'
```
**Solution:** Install Flask
```bash
pip install flask
```

### Port Already in Use
```
OSError: [Errno 48] Address already in use
```
**Solution:** Change port or kill process
```bash
lsof -ti:5000 | xargs kill -9  # Kill process on port 5000
python app.py  # Try again
```

### PWA Not Installing
- Ensure HTTPS (or localhost)
- Check manifest.json loads correctly
- Check Service Worker registered
- Clear cache and try again

## ⚡ Performance

- **Load Time:** < 1 second
- **Database:** SQLite (handles 100k+ URLs easily)
- **Concurrent Users:** Supports hundreds with gunicorn
- **Caching:** Service Worker caches static assets

### Optimize for Production

```python
# Use production WSGI server
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🗺️ Roadmap

### Version 1.0 (Current)
- [x] Basic URL shortening
- [x] Click tracking
- [x] PWA features
- [x] SQLite database

### Version 1.1 (Next)
- [ ] Custom short codes
- [ ] URL expiration
- [ ] QR code generation
- [ ] Analytics dashboard

### Version 2.0 (Future)
- [ ] User accounts
- [ ] Branded domains
- [ ] API access
- [ ] Bulk URL shortening

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing`
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

**Eugene**
- GitHub: [@eugene234466](https://github.com/eugene234466)
- Location: Accra, Ghana 🇬🇭

## 🙏 Acknowledgments

- Flask team for the amazing framework
- PWA community for the standards
- You for using this project!

## 📞 Support

- 🐛 **Bug Reports:** Open an issue
- 💡 **Feature Requests:** Open an issue
- 📧 **Email:** [your-email@example.com]

## ⭐ Show Your Support

Give a ⭐️ if this project helped you!

---

**Built with 💪 by Eugene**

*Learning mobile dev one project at a time* 🚀