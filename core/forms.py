from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, MoodEntry, Organization, OrganizationStaff

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    phone = forms.CharField(max_length=15, required=False)
    gender = forms.ChoiceField(choices=User._meta.get_field('gender').choices, required=False)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, initial='user')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'birth_date', 
                 'phone', 'gender', 'role', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})

class OrganizationRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=15, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'organization'
        if commit:
            user.save()
        return user

class OrganizationProfileForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ('organization_name', 'organization_type', 'license_number', 'address', 
                 'city', 'state', 'zip_code', 'country', 'phone', 'email', 'website',
                 'description', 'services_offered', 'operating_hours', 'emergency_services',
                 'insurance_accepted', 'languages_spoken')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'services_offered': forms.Textarea(attrs={'rows': 3}),
            'operating_hours': forms.Textarea(attrs={'rows': 2}),
            'insurance_accepted': forms.Textarea(attrs={'rows': 2}),
            'languages_spoken': forms.Textarea(attrs={'rows': 2}),
        }
    
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