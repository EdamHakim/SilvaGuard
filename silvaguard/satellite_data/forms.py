from django import forms
from .models import AreaOfInterest

class AreaOfInterestForm(forms.ModelForm):
    class Meta:
        model = AreaOfInterest
        fields = ['name', 'latitude', 'longitude', 'radius_km']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Amazon Rainforest Sector A'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. -3.4653',
                'step': 'any'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. -62.2159',
                'step': 'any'
            }),
            'radius_km': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. 10.0',
                'step': '0.1'
            }),
        }
