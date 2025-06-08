
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib import messages
from .forms import PDFUploadForm
from .models import PDFUpload
import os
from googletrans import Translator
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

def upload_pdf(request):
    translated_text = None
    
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        source_language = request.POST.get('source_language', 'auto')
        target_language = request.POST.get('language', 'te')
        
        if form.is_valid():
            pdf_upload = form.save()
            
            # Extract text from PDF
            extracted_text = extract_text_from_pdf(pdf_upload.file.path)
            
            if extracted_text:
                # Translate text
                translator = Translator()
                try:
                    if source_language == 'auto':
                        translation = translator.translate(extracted_text, dest=target_language)
                    else:
                        translation = translator.translate(extracted_text, src=source_language, dest=target_language)
                    
                    translated_text = translation.text
                    
                    # Store translated text in session for download
                    request.session['translated_text'] = translated_text
                    request.session['target_language'] = target_language
                    
                    messages.success(request, 'PDF translated successfully!')
                    
                except Exception as e:
                    messages.error(request, f'Translation failed: {str(e)}')
            else:
                messages.error(request, 'Could not extract text from PDF')
    else:
        form = PDFUploadForm()
    
    return render(request, 'upload.html', {
        'form': form,
        'translated_text': translated_text
    })

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text

def download_pdf(request):
    translated_text = request.session.get('translated_text')
    target_language = request.session.get('target_language', 'te')
    
    if not translated_text:
        raise Http404("No translated text found")
    
    # Create PDF with translated text
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Register font for better Unicode support
    try:
        font_path = os.path.join('core', 'static', 'fonts', 'NotoSans-Regular.ttf')
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('NotoSans', font_path))
            p.setFont('NotoSans', 12)
        else:
            p.setFont('Helvetica', 12)
    except:
        p.setFont('Helvetica', 12)
    
    # Write translated text to PDF
    width, height = letter
    y_position = height - 50
    
    lines = translated_text.split('\n')
    for line in lines:
        if y_position < 50:
            p.showPage()
            y_position = height - 50
            try:
                if os.path.exists(font_path):
                    p.setFont('NotoSans', 12)
                else:
                    p.setFont('Helvetica', 12)
            except:
                p.setFont('Helvetica', 12)
        
        # Handle long lines
        if len(line) > 80:
            words = line.split(' ')
            current_line = ''
            for word in words:
                if len(current_line + word) < 80:
                    current_line += word + ' '
                else:
                    p.drawString(50, y_position, current_line.strip())
                    y_position -= 20
                    current_line = word + ' '
                    if y_position < 50:
                        p.showPage()
                        y_position = height - 50
                        try:
                            if os.path.exists(font_path):
                                p.setFont('NotoSans', 12)
                            else:
                                p.setFont('Helvetica', 12)
                        except:
                            p.setFont('Helvetica', 12)
            if current_line:
                p.drawString(50, y_position, current_line.strip())
                y_position -= 20
        else:
            p.drawString(50, y_position, line)
            y_position -= 20
    
    p.save()
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="translated_{target_language}.pdf"'
    
    return response
