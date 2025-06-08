#!/usr/bin/env python3
"""
Setup script for AI-Based PDF Translator
Run this script to set up the application locally
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def create_directories():
    """Create required directories"""
    directories = ['uploads', 'downloads', 'fonts', 'instance']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'local_requirements.txt'], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("Error output:", e.stderr)
        sys.exit(1)

def setup_environment():
    """Set up environment file"""
    env_file = Path('.env')
    if not env_file.exists():
        print("🔧 Creating .env file...")
        with open('.env.example', 'r') as source:
            content = source.read()
        
        # Generate a random secret key
        import secrets
        secret_key = secrets.token_urlsafe(32)
        session_secret = secrets.token_urlsafe(32)
        
        content = content.replace('your-secret-key-here-change-this-in-production', secret_key)
        content = content.replace('your-session-secret-here', session_secret)
        
        with open('.env', 'w') as target:
            target.write(content)
        print("✅ Environment file created with random secret keys")
    else:
        print("✅ Environment file already exists")

def initialize_database():
    """Initialize the SQLite database"""
    print("🗄️ Initializing database...")
    try:
        # Create the database file and tables
        from app import app, db
        with app.app_context():
            db.create_all()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("Trying manual SQLite setup...")
        
        # Fallback: create database manually
        db_path = 'instance/pdf_translator.db'
        os.makedirs('instance', exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create translation_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS translation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id VARCHAR(128) NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                translated_filename VARCHAR(255) NOT NULL,
                source_language VARCHAR(10) NOT NULL,
                target_language VARCHAR(10) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database created manually")

def test_installation():
    """Test if the installation works"""
    print("🧪 Testing installation...")
    try:
        from pdf_processor import PDFProcessor
        processor = PDFProcessor()
        print("✅ PDF processor initialized successfully")
        
        # Test translation
        test_text = "Hello, this is a test."
        translated = processor.translate_text(test_text, 'en', 'hi')
        if translated and len(translated) > 0:
            print("✅ Translation service working")
        else:
            print("⚠️ Translation service may have issues")
            
    except Exception as e:
        print(f"⚠️ Testing failed: {e}")
        print("The application may still work, but there could be issues")

def main():
    """Main setup function"""
    print("🚀 Setting up AI-Based PDF Translator")
    print("=" * 50)
    
    check_python_version()
    create_directories()
    setup_environment()
    install_dependencies()
    initialize_database()
    test_installation()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\nTo run the application:")
    print("1. Activate your virtual environment (if using one)")
    print("2. Run: python main.py")
    print("3. Open http://localhost:5000 in your browser")
    print("\nFor production deployment:")
    print("Run: gunicorn --bind 0.0.0.0:5000 main:app")

if __name__ == "__main__":
    main()