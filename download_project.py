#!/usr/bin/env python3
"""
Download script to get all project files for local setup
This script creates a zip file with all necessary components
"""

import os
import zipfile
import shutil
from pathlib import Path

def create_project_package():
    """Create a complete project package for local installation"""
    
    # Files to include in the package
    project_files = [
        'main.py',
        'app.py', 
        'models.py',
        'routes.py',
        'pdf_processor.py',
        'setup.py',
        'run_local.py',
        'local_requirements.txt',
        '.env.example',
        'README.md',
        'INSTALL_GUIDE.md',
        'static/css/style.css',
        'static/js/app.js',
        'templates/base.html',
        'templates/index.html'
    ]
    
    # Create package directory
    package_dir = Path('pdf_translator_package')
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    print("Creating complete project package...")
    
    # Copy all files
    for file_path in project_files:
        source = Path(file_path)
        if source.exists():
            target = package_dir / file_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            print(f"✅ Added: {file_path}")
        else:
            print(f"⚠️ Missing: {file_path}")
    
    # Create placeholder directories
    directories = ['uploads', 'downloads', 'fonts', 'instance']
    for directory in directories:
        (package_dir / directory).mkdir(exist_ok=True)
        # Add .gitkeep files
        (package_dir / directory / '.gitkeep').touch()
        print(f"✅ Created directory: {directory}")
    
    # Create zip file
    zip_path = 'pdf_translator_complete.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(package_dir)
                zipf.write(file_path, arc_path)
    
    # Cleanup
    shutil.rmtree(package_dir)
    
    print(f"\n✅ Package created: {zip_path}")
    print(f"📁 Size: {os.path.getsize(zip_path) / 1024:.1f} KB")
    
    return zip_path

def create_quick_start_script():
    """Create a quick start script for Windows and Unix"""
    
    # Windows batch file
    windows_script = """@echo off
echo Setting up AI-Based PDF Translator...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\\Scripts\\activate

REM Install dependencies
echo Installing dependencies...
pip install -r local_requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

REM Run setup
echo Running setup...
python setup.py
if errorlevel 1 (
    echo Setup failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To start the application:
echo 1. Run: venv\\Scripts\\activate
echo 2. Run: python main.py
echo 3. Open: http://localhost:5000
echo.
pause
"""

    # Unix shell script
    unix_script = """#!/bin/bash
echo "Setting up AI-Based PDF Translator..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed"
    echo "Please install Python 3.8+ first"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Python 3.8+ required, found $python_version"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r local_requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies"
    exit 1
fi

# Run setup
echo "Running setup..."
python setup.py
if [ $? -ne 0 ]; then
    echo "Setup failed"
    exit 1
fi

echo
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo
echo "To start the application:"
echo "1. Run: source venv/bin/activate"
echo "2. Run: python main.py"
echo "3. Open: http://localhost:5000"
echo
"""

    # Write scripts
    with open('pdf_translator_package/quick_start.bat', 'w') as f:
        f.write(windows_script)
    
    with open('pdf_translator_package/quick_start.sh', 'w') as f:
        f.write(unix_script)
    
    # Make shell script executable
    os.chmod('pdf_translator_package/quick_start.sh', 0o755)
    
    print("✅ Created quick start scripts")

if __name__ == "__main__":
    zip_file = create_project_package()
    print(f"\n🎉 Complete project package ready: {zip_file}")
    print("\nWhat's included:")
    print("- All source code files")
    print("- Installation scripts")
    print("- Dependencies list")
    print("- Complete documentation")
    print("- Quick start scripts")
    print("\nTo use: Extract the zip file and run setup.py")