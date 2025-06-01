from django import forms
from .models import ColorizedImage

class ImageUploadForm(forms.ModelForm):
    """Form for uploading images and setting colorization parameters"""
    class Meta:
        model = ColorizedImage
        fields = ['original_image', 'color_hex', 'intensity', 'edge_smooth']
        widgets = {
            'color_hex': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'intensity': forms.NumberInput(attrs={
                'class': 'form-range', 
                'type': 'range',
                'min': '0.1',
                'max': '1.0',
                'step': '0.1'
            }),
            'edge_smooth': forms.NumberInput(attrs={
                'class': 'form-range',
                'type': 'range',
                'min': '0',
                'max': '5',
                'step': '1'
            }),
        }