import os
import uuid
from flask import render_template, request, redirect, url_for, flash, session, send_file, jsonify
from werkzeug.utils import secure_filename
from app import app, db
from models import TranslationHistory
from pdf_processor import PDFProcessor 
import logging

# Supported languages
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese (Simplified)',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'te': 'Telugu'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@app.route('/')
def index():
    # Initialize session ID if not exists
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    # Get user's translation history
    history = TranslationHistory.query.filter_by(session_id=session['session_id']).order_by(TranslationHistory.created_at.desc()).limit(10).all()
    
    return render_template('index.html', languages=LANGUAGES, history=history)

@app.route('/translate-progress/<task_id>')
def translate_progress(task_id):
    """Get translation progress for a specific task"""
    # This would be implemented with a task queue like Celery in production
    # For now, return a simple response
    return jsonify({'status': 'processing', 'progress': 50})

@app.route('/api/history')
def get_translation_history():
    """API endpoint to get recent translation history"""
    try:
        if 'session_id' not in session:
            return jsonify({'history': []})
        
        history = TranslationHistory.query.filter_by(
            session_id=session['session_id']
        ).order_by(TranslationHistory.created_at.desc()).limit(10).all()
        
        history_data = []
        for entry in history:
            history_data.append({
                'id': entry.id,
                'original_filename': entry.original_filename,
                'translated_filename': entry.translated_filename,
                'source_language': entry.source_language,
                'target_language': entry.target_language,
                'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'file_size': entry.file_size
            })
        
        return jsonify({'history': history_data})
    except Exception as e:
        logging.error(f"Error getting history: {e}")
        return jsonify({'history': [], 'error': str(e)})

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Debug logging
        logging.debug(f"Form data keys: {list(request.form.keys())}")
        logging.debug(f"Files keys: {list(request.files.keys())}")
        logging.debug(f"Content type: {request.content_type}")
        logging.debug(f"Content length: {request.content_length}")
        
        # Check if file was uploaded
        if 'file' not in request.files:
            logging.error("No 'file' field in request.files")
            flash('No file was uploaded. Please select a PDF file.', 'error')
            return redirect(url_for('index'))
        
        file = request.files['file']
        source_lang = request.form.get('source_language')
        target_lang = request.form.get('target_language')
        
        logging.debug(f"File object: {file}")
        logging.debug(f"Filename: '{file.filename}'")
        logging.debug(f"File size: {file.content_length if hasattr(file, 'content_length') else 'unknown'}")
        logging.debug(f"Source language: '{source_lang}'")
        logging.debug(f"Target language: '{target_lang}'")
        
        # Check if filename is empty
        if not file.filename or file.filename == '':
            logging.error(f"Empty or missing filename: '{file.filename}'")
            flash('Please select a valid PDF file.', 'error')
            return redirect(url_for('index'))
        
        # Check if file content exists
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size == 0:
            logging.error("Uploaded file is empty")
            flash('The uploaded file appears to be empty.', 'error')
            return redirect(url_for('index'))
        
        if not source_lang or not target_lang:
            flash('Please select both source and target languages', 'error')
            return redirect(url_for('index'))
        
        if source_lang == target_lang:
            flash('Source and target languages cannot be the same', 'error')
            return redirect(url_for('index'))
        
        if file and allowed_file(file.filename):
            # Secure the filename
            original_filename = secure_filename(file.filename)
            
            # Create unique filename to avoid conflicts
            file_id = str(uuid.uuid4())
            upload_filename = f"{file_id}_{original_filename}"
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], upload_filename)
            
            # Save uploaded file
            file.save(upload_path)
            file_size = os.path.getsize(upload_path)
            
            # Process PDF translation
            processor = PDFProcessor()
            
            try:
                # Extract text from PDF
                logging.info("Starting text extraction...")
                text_content = processor.extract_text(upload_path)
                
                if not text_content.strip():
                    flash('No readable text found in the PDF', 'error')
                    os.remove(upload_path)  # Clean up
                    return redirect(url_for('index'))
                
                logging.info(f"Extracted {len(text_content)} characters from PDF")
                
                # Translate text
                logging.info(f"Starting translation from {source_lang} to {target_lang}")
                translated_text = processor.translate_text(text_content, source_lang, target_lang)
                
                # Generate translated PDF
                logging.info("Generating translated PDF...")
                translated_filename = f"translated_{file_id}_{original_filename}"
                translated_path = os.path.join(app.config['DOWNLOAD_FOLDER'], translated_filename)
                
                processor.create_pdf(translated_text, translated_path, original_filename, target_lang)
                
                # Clean up uploaded file immediately
                os.remove(upload_path)
                
                # Save to history immediately but efficiently
                session_id = session.get('session_id', str(uuid.uuid4()))
                session['session_id'] = session_id
                
                try:
                    history_entry = TranslationHistory()
                    history_entry.session_id = session_id
                    history_entry.original_filename = original_filename
                    history_entry.translated_filename = translated_filename
                    history_entry.source_language = source_lang
                    history_entry.target_language = target_lang
                    history_entry.file_size = file_size
                    db.session.add(history_entry)
                    db.session.commit()
                    logging.info("Translation history saved successfully")
                except Exception as db_error:
                    logging.warning(f"History save failed: {db_error}")
                    db.session.rollback()
                    # Continue without failing the request
                
                flash(f'PDF successfully translated from {LANGUAGES[source_lang]} to {LANGUAGES[target_lang]}!', 'success')
                return redirect(url_for('download_file', filename=translated_filename))
                
            except Exception as e:
                logging.error(f"Translation error: {str(e)}")
                flash(f'Translation failed: {str(e)}', 'error')
                # Clean up files
                if os.path.exists(upload_path):
                    os.remove(upload_path)
                return redirect(url_for('index'))
        else:
            flash('Please upload a valid PDF file', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        flash('An error occurred during file upload', 'error')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            flash('File not found', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        logging.error(f"Download error: {str(e)}")
        flash('Error downloading file', 'error')
        return redirect(url_for('index'))

@app.route('/clear_history')
def clear_history():
    try:
        # Delete history entries for current session
        TranslationHistory.query.filter_by(session_id=session.get('session_id', '')).delete()
        db.session.commit()
        flash('History cleared successfully', 'success')
    except Exception as e:
        logging.error(f"Clear history error: {str(e)}")
        flash('Error clearing history', 'error')
    
    return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('index'))
