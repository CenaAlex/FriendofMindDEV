"""
Forms for Mental Health Resources
"""
from django import forms
from .models import MentalHealthResource, ResourceCategory


class MentalHealthResourceForm(forms.ModelForm):
    """Form for creating/editing mental health resources"""
    class Meta:
        model = MentalHealthResource
        fields = [
            'title', 'description', 'resource_type', 'category',
            'url', 'phone_number', 'email', 'address',
            'is_free', 'is_24_7', 'languages_supported',
            'is_verified', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Resource title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Detailed description of the resource...'
            }),
            'resource_type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@example.com'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Physical address (if applicable)'
            }),
            'languages_supported': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'English, Filipino, Spanish'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make optional fields clearly marked
        self.fields['url'].required = False
        self.fields['phone_number'].required = False
        self.fields['email'].required = False
        self.fields['address'].required = False

