from django.shortcuts import render, redirect
from django.http import FileResponse
from .forms import PDFUploadForm
from .models import PDFUpload
from googletrans import Translator
from reportlab.pdfgen import canvas
import io
import fitz  # PyMuPDF

def upload_pdf(request):
    text = None
    translated_text = None

    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf = form.save()
            file_path = pdf.file.path

            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()

            translator = Translator()
            translated = translator.translate(text, src='auto', dest='te')  # Telugu
            translated_text = translated.text

            # If "Download PDF" button was clicked
            if 'download' in request.POST:
                return generate_pdf_response(translated_text)
    else:
        form = PDFUploadForm()

    return render(request, 'upload.html', {
        'form': form,
        'text': text,
        'translated_text': translated_text
    })

def generate_pdf_response(translated_text):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    y = 800
    for line in translated_text.split('\n'):
        p.drawString(50, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            y = 800
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='translated.pdf')
