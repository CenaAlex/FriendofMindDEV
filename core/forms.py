from django import forms
from django.contrib.auth.forms import UserCreationForm
import re
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
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            # Only allow letters, spaces, hyphens, and apostrophes
            if not re.match(r"^[A-Za-z\s'-]+$", first_name):
                raise forms.ValidationError("First name can only contain letters, spaces, hyphens, and apostrophes.")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            # Only allow letters, spaces, hyphens, and apostrophes
            if not re.match(r"^[A-Za-z\s'-]+$", last_name):
                raise forms.ValidationError("Last name can only contain letters, spaces, hyphens, and apostrophes.")
        return last_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Django's EmailField already validates format, but we can add additional check
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                raise forms.ValidationError("Please enter a valid email address (e.g., name@example.com).")
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("This email address is already registered. Please use a different email or try logging in.")
        return email

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
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            if not re.match(r"^[A-Za-z\s'-]+$", first_name):
                raise forms.ValidationError("First name can only contain letters, spaces, hyphens, and apostrophes.")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            if not re.match(r"^[A-Za-z\s'-]+$", last_name):
                raise forms.ValidationError("Last name can only contain letters, spaces, hyphens, and apostrophes.")
        return last_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                raise forms.ValidationError("Please enter a valid email address (e.g., name@example.com).")
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("This email address is already registered. Please use a different email or try logging in.")
        return email
    
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
        fields = ('first_name', 'last_name', 'birth_date', 'phone', 
                 'gender', 'occupation', 'emergency_contact', 'emergency_phone')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            if not re.match(r"^[A-Za-z\s'-]+$", first_name):
                raise forms.ValidationError("First name can only contain letters, spaces, hyphens, and apostrophes.")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            if not re.match(r"^[A-Za-z\s'-]+$", last_name):
                raise forms.ValidationError("Last name can only contain letters, spaces, hyphens, and apostrophes.")
        return last_name
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Allow numbers, spaces, hyphens, parentheses, and + for international format
            if not re.match(r"^[\d\s\-\(\)\+]+$", phone):
                raise forms.ValidationError("Phone number can only contain numbers, spaces, hyphens, parentheses, and + sign.")
        return phone
    
    def clean_emergency_contact(self):
        emergency_contact = self.cleaned_data.get('emergency_contact')
        if emergency_contact:
            if not re.match(r"^[A-Za-z\s'-]+$", emergency_contact):
                raise forms.ValidationError("Emergency contact name can only contain letters, spaces, hyphens, and apostrophes.")
        return emergency_contact
    
    def clean_emergency_phone(self):
        emergency_phone = self.cleaned_data.get('emergency_phone')
        if emergency_phone:
            # Allow numbers, spaces, hyphens, parentheses, and + for international format
            if not re.match(r"^[\d\s\-\(\)\+]+$", emergency_phone):
                raise forms.ValidationError("Emergency phone number can only contain numbers, spaces, hyphens, parentheses, and + sign.")
        return emergency_phone
    
    def clean_occupation(self):
        occupation = self.cleaned_data.get('occupation')
        if occupation:
            # Allow letters, numbers, spaces, hyphens, and apostrophes for job titles
            if not re.match(r"^[A-Za-z0-9\s'-]+$", occupation):
                raise forms.ValidationError("Occupation can only contain letters, numbers, spaces, hyphens, and apostrophes.")
        return occupation

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

class AdminOrganizationCreationForm(forms.Form):
    """Form for admins to manually create organization accounts"""
    
    # User Account Fields
    username = forms.CharField(
        max_length=150,
        help_text="Username for the organization account"
    )
    email = forms.EmailField(
        help_text="Primary email address for the organization"
    )
    first_name = forms.CharField(
        max_length=30,
        help_text="Contact person's first name"
    )
    last_name = forms.CharField(
        max_length=30,
        help_text="Contact person's last name"
    )
    phone = forms.CharField(
        max_length=20,
        help_text="Primary contact phone number"
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Initial password for the organization account"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password",
        help_text="Confirm the password"
    )
    
    # Organization Profile Fields
    organization_name = forms.CharField(
        max_length=200,
        help_text="Official organization name"
    )
    organization_type = forms.ChoiceField(
        choices=Organization._meta.get_field('organization_type').choices,
        help_text="Type of mental health organization"
    )
    license_number = forms.CharField(
        max_length=100,
        required=False,
        help_text="Professional license number (if applicable)"
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Full street address"
    )
    city = forms.CharField(
        max_length=100,
        help_text="City"
    )
    state = forms.CharField(
        max_length=100,
        help_text="State or Province"
    )
    zip_code = forms.CharField(
        max_length=20,
        help_text="ZIP or Postal Code"
    )
    country = forms.CharField(
        max_length=100,
        initial="Philippines",
        help_text="Country"
    )
    organization_phone = forms.CharField(
        max_length=20,
        help_text="Organization main phone number"
    )
    organization_email = forms.EmailField(
        help_text="Organization official email (can be same as user email)"
    )
    website = forms.URLField(
        required=False,
        help_text="Organization website URL (optional)"
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        help_text="Brief description of the organization and its mission"
    )
    services_offered = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Services offered by the organization"
    )
    operating_hours = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        help_text="Operating hours (e.g., Mon-Fri 9AM-5PM)"
    )
    emergency_services = forms.BooleanField(
        required=False,
        help_text="Does the organization provide emergency services?"
    )
    insurance_accepted = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        help_text="Insurance plans accepted"
    )
    languages_spoken = forms.CharField(
        max_length=200,
        initial="English, Filipino",
        help_text="Languages spoken at the organization"
    )
    is_verified = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Mark organization as verified upon creation"
    )
    send_welcome_email = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Send welcome email with login credentials"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'style': 'margin-bottom: 10px;'
            })
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        
        # Check if username already exists
        username = cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError(f"Username '{username}' already exists.")
        
        # Check if email already exists
        email = cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(f"Email '{email}' is already registered.")
        
        return cleaned_data
    
    def save(self):
        """Create the user and organization profile"""
        from django.contrib.auth.hashers import make_password
        
        # Create the user account
        user = User.objects.create(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            phone=self.cleaned_data['phone'],
            password=make_password(self.cleaned_data['password']),
            role='organization',
            is_active=True
        )
        
        # Create the organization profile
        organization = Organization.objects.create(
            user=user,
            organization_name=self.cleaned_data['organization_name'],
            organization_type=self.cleaned_data['organization_type'],
            license_number=self.cleaned_data.get('license_number', ''),
            address=self.cleaned_data['address'],
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
            zip_code=self.cleaned_data['zip_code'],
            country=self.cleaned_data['country'],
            phone=self.cleaned_data['organization_phone'],
            email=self.cleaned_data['organization_email'],
            website=self.cleaned_data.get('website', ''),
            description=self.cleaned_data.get('description', ''),
            services_offered=self.cleaned_data.get('services_offered', ''),
            operating_hours=self.cleaned_data.get('operating_hours', ''),
            emergency_services=self.cleaned_data.get('emergency_services', False),
            insurance_accepted=self.cleaned_data.get('insurance_accepted', ''),
            languages_spoken=self.cleaned_data['languages_spoken'],
            is_verified=self.cleaned_data.get('is_verified', False)
        )
        
        return user, organization

class AdminUserEditForm(forms.ModelForm):
    """Form for admins to edit user accounts"""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'birth_date', 
                 'phone', 'gender', 'occupation', 'emergency_contact', 'emergency_phone',
                 'role', 'is_active', 'is_staff', 'is_superuser')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class AdminUserCreateForm(forms.ModelForm):
    """Form for admins to create new user accounts"""
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Initial password for the user account"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password",
        help_text="Confirm the password"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'birth_date', 
                 'phone', 'gender', 'occupation', 'emergency_contact', 'emergency_phone',
                 'role', 'is_active', 'is_staff')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        # Set defaults
        self.fields['is_active'].initial = True
        self.fields['role'].initial = 'user'
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        
        # Check if username already exists
        username = cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError(f"Username '{username}' already exists.")
        
        return cleaned_data
    
    def save(self, commit=True):
        from django.contrib.auth.hashers import make_password
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class AdminOrganizationEditForm(forms.ModelForm):
    """Form for admins to edit organization profiles"""
    class Meta:
        model = Organization
        fields = ('organization_name', 'organization_type', 'license_number', 'address', 
                 'city', 'state', 'zip_code', 'country', 'phone', 'email', 'website',
                 'description', 'services_offered', 'operating_hours', 'emergency_services',
                 'insurance_accepted', 'languages_spoken', 'is_verified')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'services_offered': forms.Textarea(attrs={'rows': 3}),
            'operating_hours': forms.Textarea(attrs={'rows': 2}),
            'insurance_accepted': forms.Textarea(attrs={'rows': 2}),
            'languages_spoken': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})