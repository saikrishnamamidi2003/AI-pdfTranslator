# AI-Based PDF Translator

A Flask-based web application for translating PDF documents across multiple languages with Unicode font support.

## Features

- **Multi-language Support**: English, Hindi, Telugu, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese, Arabic
- **Drag & Drop Interface**: Easy PDF upload with visual feedback
- **High-Quality Fonts**: Unicode fonts for proper rendering of Hindi, Telugu, and other scripts
- **Fast Translation**: Optimized processing completing in under 2 seconds
- **Translation History**: Session-based history tracking with download links
- **Real-time Updates**: Automatic history refresh without page reload

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL (optional - uses SQLite by default)

### Local Setup

1. **Clone or Download the Project**
   ```bash
   git clone <repository-url>
   cd pdf-translator
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**
   Create a `.env` file in the project root:
   ```
   FLASK_SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///pdf_translator.db
   FLASK_ENV=development
   ```

5. **Initialize Database**
   ```bash
   python -c "
   from app import app, db
   with app.app_context():
       db.create_all()
   print('Database initialized successfully!')
   "
   ```

6. **Create Required Directories**
   ```bash
   mkdir -p uploads downloads fonts instance
   ```

7. **Run the Application**
   ```bash
   python main.py
   ```

   Or using Gunicorn (production):
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reload main:app
   ```

8. **Access the Application**
   Open your browser and go to: `http://localhost:5000`

## Project Structure

```
pdf-translator/
├── main.py                 # Application entry point
├── app.py                  # Flask app configuration
├── models.py               # Database models
├── routes.py               # Application routes
├── pdf_processor.py        # PDF processing logic
├── requirements.txt        # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css      # Application styles
│   └── js/
│       └── app.js         # Frontend JavaScript
├── templates/
│   ├── base.html          # Base template
│   └── index.html         # Main application page
├── uploads/               # Temporary upload directory
├── downloads/             # Translated PDFs storage
├── fonts/                 # Unicode fonts (auto-downloaded)
└── instance/              # Database files
```

## Configuration

### Database Options

**SQLite (Default)**
```python
DATABASE_URL=sqlite:///pdf_translator.db
```

**PostgreSQL**
```python
DATABASE_URL=postgresql://username:password@localhost/pdf_translator
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| FLASK_SECRET_KEY | Session encryption key | Required |
| DATABASE_URL | Database connection string | sqlite:///pdf_translator.db |
| FLASK_ENV | Environment mode | production |
| MAX_CONTENT_LENGTH | Max upload size | 16MB |

## Dependencies

### Python Packages
- Flask 2.3.3
- Flask-SQLAlchemy 3.0.5
- PyMuPDF (fitz) 1.23.8
- googletrans 4.0.0rc1
- ReportLab 4.0.4
- Gunicorn 21.2.0

### Font Dependencies
The application automatically downloads Unicode fonts:
- Noto Sans (General text)
- Noto Sans Devanagari (Hindi)
- Noto Serif Telugu (Telugu - improved quality)
- Noto Sans Telugu Bold (Telugu emphasis)

## Usage

1. **Upload PDF**: Drag and drop or click to select a PDF file
2. **Select Languages**: Choose source and target languages
3. **Translate**: Click "Translate PDF" button
4. **Download**: Access translated PDF via download link or history
5. **History**: View recent translations in the history section

## API Endpoints

- `GET /` - Main application page
- `POST /upload` - File upload and translation
- `GET /download/<filename>` - Download translated files
- `GET /api/history` - Get translation history (JSON)
- `POST /clear-history` - Clear translation history

## Troubleshooting

### Common Issues

**Font Rendering Problems**
- Fonts are downloaded automatically on first use
- Check internet connection for font downloads
- Verify `fonts/` directory has write permissions

**Translation Errors**
- Ensure internet connection for Google Translate API
- Check file format (only PDF supported)
- Verify file size under 16MB limit

**Database Issues**
- Delete `instance/pdf_translator.db` and restart
- Check database permissions
- Verify DATABASE_URL format

### Performance Optimization

**For Large Files**
- Increase `MAX_CONTENT_LENGTH` in configuration
- Consider using Celery for background processing
- Implement file chunking for very large documents

**For High Traffic**
- Use Redis for session storage
- Implement caching for translated content
- Use CDN for static assets

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development
python main.py
```

### Adding New Languages
1. Update `LANGUAGES` dictionary in `routes.py`
2. Add corresponding font support in `pdf_processor.py`
3. Update frontend language options in templates

### Testing
```bash
python test_pdf.py  # Create test PDF
python -c "from pdf_processor import PDFProcessor; PDFProcessor().extract_text('test.pdf')"
```

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Ensure proper file permissions
4. Check application logs for detailed error messages