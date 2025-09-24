from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, MoodEntry

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    phone = forms.CharField(max_length=15, required=False)
    gender = forms.ChoiceField(choices=User._meta.get_field('gender').choices, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'birth_date', 
                 'phone', 'gender', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'birth_date', 'phone', 
                 'gender', 'occupation', 'emergency_contact', 'emergency_phone')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})

class MoodEntryForm(forms.ModelForm):
    class Meta:
        model = MoodEntry
        fields = ('mood', 'notes')
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'How are you feeling today? (optional)'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})