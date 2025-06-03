from googletrans import Translator

def upload_pdf(request):
    text = None
    translated_text = None
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf = form.save()
            file_path = pdf.file.path

            import fitz
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()

            # Translate the extracted text
            translator = Translator()
            translated = translator.translate(text, src='auto', dest='te')  # Telugu
            translated_text = translated.text
    else:
        form = PDFUploadForm()

    return render(request, 'upload.html', {
        'form': form,
        'text': text,
        'translated_text': translated_text
    })