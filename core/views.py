from django.shortcuts import render
from .models import PDFUpload
from .forms import PDFUploadForm
import fitz  # PyMuPDF

def upload_pdf(request):
    text = None
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf = form.save()
            # extract text from the uploaded file
            file_path = pdf.file.path
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
    else:
        form = PDFUploadForm()

    return render(request, 'upload.html', {'form': form, 'text': text})
