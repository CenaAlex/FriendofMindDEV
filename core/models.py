from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'Regular User'),
        ('organization', 'Organization'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=20, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ], blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    notifications_enabled = models.BooleanField(default=True)
    privacy_settings = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class MoodEntry(models.Model):
    MOOD_CHOICES = [
        (1, 'Very Sad'),
        (2, 'Sad'),
        (3, 'Neutral'),
        (4, 'Happy'),
        (5, 'Very Happy')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood = models.IntegerField(choices=MOOD_CHOICES)
    notes = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_mood_display()} on {self.date.date()}"

class Organization(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='organization_profile')
    organization_name = models.CharField(max_length=200)
    organization_type = models.CharField(max_length=100, choices=[
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
        ('counseling_center', 'Counseling Center'),
        ('mental_health_center', 'Mental Health Center'),
        ('ngo', 'Non-Governmental Organization'),
        ('government_agency', 'Government Agency'),
        ('private_practice', 'Private Practice'),
        ('other', 'Other')
    ])
    license_number = models.CharField(max_length=100, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Philippines')
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    services_offered = models.TextField(blank=True)
    operating_hours = models.TextField(blank=True)
    emergency_services = models.BooleanField(default=False)
    insurance_accepted = models.TextField(blank=True)
    languages_spoken = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    verification_documents = models.FileField(upload_to='organization_docs/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.organization_name
    
    @property
    def full_address(self):
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}, {self.country}"

class OrganizationStaff(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='staff')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organization_staff')
    role = models.CharField(max_length=50, choices=[
        ('admin', 'Administrator'),
        ('counselor', 'Counselor'),
        ('psychologist', 'Psychologist'),
        ('psychiatrist', 'Psychiatrist'),
        ('social_worker', 'Social Worker'),
        ('nurse', 'Nurse'),
        ('receptionist', 'Receptionist'),
        ('other', 'Other')
    ])
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['organization', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role} at {self.organization.organization_name}"