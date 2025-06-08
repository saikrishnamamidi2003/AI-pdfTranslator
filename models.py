from app import db
from datetime import datetime

class TranslationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(128), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    translated_filename = db.Column(db.String(255), nullable=False)
    source_language = db.Column(db.String(10), nullable=False)
    target_language = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_size = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<TranslationHistory {self.original_filename} -> {self.translated_filename}>'
