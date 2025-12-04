from django import forms
from .models import Book


class ExampleForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'library']

    def clean_title(self):
        # Basic sanitization: strip whitespace; additional checks can be added
        title = self.cleaned_data.get('title', '')
        return title.strip()
