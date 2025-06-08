# Complete Local Installation Guide

## Quick Start (5 minutes)

### Option 1: Automated Setup
```bash
# 1. Download all project files to a folder
# 2. Open terminal in the project folder
# 3. Run the setup script
python setup.py
python run_local.py
```

### Option 2: Manual Setup
```bash
# 1. Create virtual environment
python -m venv pdf_translator_env
source pdf_translator_env/bin/activate  # On Windows: pdf_translator_env\Scripts\activate

# 2. Install dependencies
pip install -r local_requirements.txt

# 3. Create directories
mkdir uploads downloads fonts instance

# 4. Set up environment
cp .env.example .env
# Edit .env file with your preferred settings

# 5. Initialize database
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# 6. Run application
python main.py
```

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: 512MB minimum, 1GB recommended
- **Storage**: 100MB for application + space for uploaded/translated files
- **Internet**: Required for Google Translate API and font downloads

## File Structure for Local Setup

```
your-project-folder/
├── main.py                 # Start the application
├── app.py                  # Flask configuration
├── models.py               # Database models
├── routes.py               # URL routes and handlers
├── pdf_processor.py        # PDF processing and translation
├── setup.py               # Automated setup script
├── run_local.py           # Local development runner
├── local_requirements.txt # Python dependencies
├── .env.example          # Environment template
├── .env                  # Your environment settings (created during setup)
├── README.md             # Full documentation
├── INSTALL_GUIDE.md      # This installation guide
├── static/
│   ├── css/
│   │   └── style.css     # Application styling
│   └── js/
│       └── app.js        # Frontend JavaScript
├── templates/
│   ├── base.html         # HTML template base
│   └── index.html        # Main application page
├── uploads/              # Temporary file uploads (auto-created)
├── downloads/            # Translated PDFs (auto-created)
├── fonts/                # Unicode fonts (auto-downloaded)
└── instance/             # Database files (auto-created)
```

## Detailed Installation Steps

### 1. Python Installation
- **Windows**: Download from python.org, check "Add to PATH"
- **macOS**: `brew install python3` or download from python.org
- **Linux**: `sudo apt install python3 python3-pip python3-venv`

### 2. Project Setup
```bash
# Create project directory
mkdir pdf-translator
cd pdf-translator

# Download/copy all project files here
# (Copy all .py files, static/, templates/, and config files)
```

### 3. Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Your prompt should now show (venv)
```

### 4. Install Dependencies
```bash
pip install Flask==2.3.3
pip install Flask-SQLAlchemy==3.0.5
pip install PyMuPDF==1.23.8
pip install googletrans==4.0.0rc1
pip install reportlab==4.0.4
pip install gunicorn==21.2.0
pip install psycopg2-binary==2.9.7
pip install Werkzeug==2.3.7
pip install email-validator==2.0.0
pip install SQLAlchemy==2.0.21

# Or install all at once:
pip install -r local_requirements.txt
```

### 5. Environment Configuration
Create `.env` file:
```bash
# Copy the example
cp .env.example .env

# Edit .env file with your settings:
FLASK_SECRET_KEY=your-random-secret-key-here
DATABASE_URL=sqlite:///instance/pdf_translator.db
FLASK_ENV=development
```

### 6. Database Setup
```bash
# Create database
python -c "
from app import app, db
with app.app_context():
    db.create_all()
print('Database created successfully!')
"
```

### 7. Run the Application
```bash
# Development mode
python main.py

# Or using the local runner
python run_local.py

# Production mode with Gunicorn
gunicorn --bind 0.0.0.0:5000 main:app
```

### 8. Access the Application
Open your web browser and go to: **http://localhost:5000**

## Troubleshooting

### Common Installation Issues

**"ModuleNotFoundError"**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r local_requirements.txt
```

**"Permission Denied" Errors**
```bash
# On Linux/macOS, ensure proper permissions
chmod +x setup.py run_local.py
sudo chown -R $USER:$USER .
```

**Database Errors**
```bash
# Delete and recreate database
rm -rf instance/
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

**Port 5000 Already in Use**
```bash
# Kill existing process
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# macOS/Linux:
lsof -ti:5000 | xargs kill -9

# Or use different port
python -c "from app import app; app.run(port=8000)"
```

### Font Issues
Fonts are downloaded automatically when first needed. If you encounter font problems:
```bash
# Clear font cache
rm -rf fonts/
# Restart application - fonts will re-download
```

### Translation Service Issues
The application uses Google Translate's free service. If translations fail:
- Check internet connection
- Verify no firewall blocking
- Try smaller PDF files first
- Wait a moment between translations

## Production Deployment

### Environment Variables for Production
```bash
FLASK_SECRET_KEY=very-secure-random-key
DATABASE_URL=postgresql://user:pass@localhost/pdf_translator
FLASK_ENV=production
MAX_CONTENT_LENGTH=16777216
```

### Using PostgreSQL (Optional)
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib  # Linux
brew install postgresql  # macOS

# Create database
sudo -u postgres createdb pdf_translator

# Update .env
DATABASE_URL=postgresql://username:password@localhost/pdf_translator
```

### Systemd Service (Linux Production)
Create `/etc/systemd/system/pdf-translator.service`:
```ini
[Unit]
Description=PDF Translator
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/pdf-translator
Environment=PATH=/path/to/pdf-translator/venv/bin
ExecStart=/path/to/pdf-translator/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## Performance Optimization

### For Large Files
- Increase `MAX_CONTENT_LENGTH` in .env
- Use SSD storage for faster file operations
- Implement Redis for session storage

### For Multiple Users
- Use PostgreSQL instead of SQLite
- Implement reverse proxy (Nginx)
- Add Redis for caching
- Use CDN for static files

## Support

If you encounter issues:
1. Check this troubleshooting guide
2. Verify all dependencies are installed correctly
3. Ensure Python version is 3.8+
4. Check file permissions
5. Review application logs for specific error messages

The application logs will show in the terminal where you started it.