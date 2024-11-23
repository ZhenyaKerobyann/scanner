from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class URLInputForm(forms.Form):
    url = forms.URLField(
        label="Enter URL",
        widget=forms.URLInput(attrs={'placeholder': 'https://example.com'}),
        required=True
    )

    # Optional: additional URL validation if needed
    def clean_url(self):
        url = self.cleaned_data.get('url')
        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:
            raise forms.ValidationError("Invalid URL. Please enter a valid URL.")
        return url
