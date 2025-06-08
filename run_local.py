#!/usr/bin/env python3
"""
Local development runner for AI-Based PDF Translator
This script handles environment setup and runs the Flask application
"""

import os
import sys
from pathlib import Path

def load_environment():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    else:
        # Set default values for local development
        os.environ.setdefault('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
        os.environ.setdefault('DATABASE_URL', 'sqlite:///instance/pdf_translator.db')
        os.environ.setdefault('FLASK_ENV', 'development')

def ensure_directories():
    """Ensure required directories exist"""
    directories = ['uploads', 'downloads', 'fonts', 'instance', 'static/css', 'static/js', 'templates']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def main():
    """Main entry point for local development"""
    print("Starting AI-Based PDF Translator (Local Development)")
    
    # Load environment and create directories
    load_environment()
    ensure_directories()
    
    # Import and run the Flask app
    try:
        from app import app
        
        # Initialize database if needed
        from app import db
        with app.app_context():
            db.create_all()
            print("Database initialized")
        
        print("Server starting on http://localhost:5000")
        print("Press Ctrl+C to stop the server")
        
        # Run the development server
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()