from django import forms
from .models import PDFUpload

LANGUAGE_CHOICES = [
    ('en', 'English'),
    ('te', 'Telugu'),
    ('hi', 'Hindi'),
    ('fr', 'French'),
]

class PDFUploadForm(forms.ModelForm):
    target_language = forms.ChoiceField(choices=LANGUAGE_CHOICES, required=True)

    class Meta:
        model = PDFUpload
        fields = ['file']
