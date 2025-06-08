#!/usr/bin/env python3
"""
Test script to create a simple PDF for testing the translation functionality
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def create_test_pdf():
    """Create a simple test PDF with English text"""
    filename = "test_document.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Test content in English
    content = [
        Paragraph("Test Document for Translation", styles['Title']),
        Paragraph("This is a simple test document written in English.", styles['Normal']),
        Paragraph("It contains multiple paragraphs to test the translation functionality.", styles['Normal']),
        Paragraph("The PDF translator should extract this text, translate it to the target language, and create a new PDF document.", styles['Normal']),
        Paragraph("This test helps verify that the entire workflow is functioning correctly.", styles['Normal']),
    ]
    
    doc.build(content)
    print(f"Created test PDF: {filename}")
    return filename

if __name__ == "__main__":
    create_test_pdf()