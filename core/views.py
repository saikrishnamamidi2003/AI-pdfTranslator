from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import PDFUploadForm
from .models import PDFUpload

from googletrans import Translator
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os


def upload_pdf(request):
    text = None
    translated_text = None

    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf = form.save()
            file_path = pdf.file.path

            # Extract text from PDF
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()

            # Translate the text
            translator = Translator()
            translated = translator.translate(text, src='auto', dest='te')  # Telugu
            translated_text = translated.text

            # Store in session for download
            request.session['translated_text'] = translated_text
    else:
        form = PDFUploadForm()

    return render(request, 'upload.html', {
        'form': form,
        'text': text,
        'translated_text': translated_text
    })


def download_translated_pdf(request):
    translated_text = request.session.get('translated_text')
    if not translated_text:
        return redirect('/')

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Path to font file (adjust if needed)
    font_path = os.path.join('core', 'static', 'fonts', 'NotoSans-Regular.ttf')

    # Register and set font
    pdfmetrics.registerFont(TTFont('NotoSans', font_path))
    p.setFont('NotoSans', 12)

    y = 800
    for line in translated_text.split('\n'):
        p.drawString(50, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            p.setFont('NotoSans', 12)
            y = 800

    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="translated_output.pdf"'
    return response
