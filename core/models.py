
from django.db import models

class PDFUpload(models.Model):
    file = models.FileField(upload_to='pdfs/')
    translated_file = models.FileField(upload_to='translated/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
