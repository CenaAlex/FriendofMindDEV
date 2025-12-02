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

class PatientCase(models.Model):
    PRIORITY_LEVELS = [
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('monitoring', 'Monitoring'),
        ('resolved', 'Resolved'),
        ('referred', 'Referred'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='patient_cases')
    patient_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_cases')
    assigned_staff = models.ForeignKey(OrganizationStaff, on_delete=models.SET_NULL, null=True, blank=True)
    case_number = models.CharField(max_length=20, unique=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    initial_assessment_date = models.DateTimeField(default=timezone.now)
    last_contact_date = models.DateTimeField(null=True, blank=True)
    next_followup_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"Case {self.case_number} - {self.patient_user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.case_number:
            # Generate unique case number
            import random
            import string
            while True:
                case_num = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not PatientCase.objects.filter(case_number=case_num).exists():
                    self.case_number = case_num
                    break
        super().save(*args, **kwargs)

class OrganizationAppointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    APPOINTMENT_TYPES = [
        ('consultation', 'Initial Consultation'),
        ('followup', 'Follow-up'),
        ('therapy', 'Therapy Session'),
        ('assessment', 'Assessment'),
        ('group_session', 'Group Session'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='appointments')
    patient_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    staff_member = models.ForeignKey(OrganizationStaff, on_delete=models.CASCADE, related_name='appointments')
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPES)
    scheduled_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    is_online = models.BooleanField(default=False)
    meeting_link = models.URLField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"{self.get_appointment_type_display()} - {self.patient_user.get_full_name()} on {self.scheduled_date.strftime('%Y-%m-%d %H:%M')}"

class OrganizationAlert(models.Model):
    ALERT_TYPES = [
        ('high_risk_patient', 'High Risk Patient'),
        ('missed_appointment', 'Missed Appointment'),
        ('followup_due', 'Follow-up Due'),
        ('system_notification', 'System Notification'),
    ]
    
    SEVERITY_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=25, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='info')
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    related_case = models.ForeignKey(PatientCase, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.title}"

# Import feedback and notification models
from .feedback_models import Feedback, FeedbackResponse, Notification

# Import forum models
from .forum_models import ForumPost, ForumComment, ForumLike, ForumReport, ForumCommentReport