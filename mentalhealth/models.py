from django.db import models
from django.utils import timezone
from core.models import User

class ResourceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Font Awesome class
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Resource Categories"
    
    def __str__(self):
        return self.name

class MentalHealthResource(models.Model):
    RESOURCE_TYPES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('exercise', 'Exercise'),
        ('meditation', 'Meditation'),
        ('contact', 'Professional Contact'),
        ('hotline', 'Crisis Hotline'),
        ('app', 'Mobile App'),
        ('book', 'Book/Publication')
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE)
    url = models.URLField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_free = models.BooleanField(default=True)
    is_24_7 = models.BooleanField(default=False)
    languages_supported = models.CharField(max_length=200, default='English, Filipino')
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class ProfessionalContact(models.Model):
    SPECIALIZATIONS = [
        ('clinical_psychologist', 'Clinical Psychologist'),
        ('psychiatrist', 'Psychiatrist'),
        ('counselor', 'Counselor'),
        ('therapist', 'Therapist'),
        ('social_worker', 'Social Worker'),
        ('peer_support', 'Peer Support Specialist')
    ]
    
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=30, choices=SPECIALIZATIONS)
    license_number = models.CharField(max_length=50, blank=True)
    clinic_name = models.CharField(max_length=200, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    accepts_insurance = models.BooleanField(default=False)
    languages = models.CharField(max_length=200, default='English, Filipino')
    available_days = models.CharField(max_length=100, blank=True)
    available_hours = models.CharField(max_length=100, blank=True)
    is_telehealth = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.get_specialization_display()}"

class UserResourceInteraction(models.Model):
    INTERACTION_TYPES = [
        ('viewed', 'Viewed'),
        ('bookmarked', 'Bookmarked'),
        ('rated', 'Rated'),
        ('shared', 'Shared'),
        ('contacted', 'Contacted')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.ForeignKey(MentalHealthResource, on_delete=models.CASCADE, null=True, blank=True)
    professional = models.ForeignKey(ProfessionalContact, on_delete=models.CASCADE, null=True, blank=True)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    rating = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        if self.resource:
            return f"{self.user.username} {self.interaction_type} {self.resource.title}"
        elif self.professional:
            return f"{self.user.username} {self.interaction_type} {self.professional.name}"
        return f"{self.user.username} - {self.interaction_type}"

class SelfHelpExercise(models.Model):
    EXERCISE_TYPES = [
        ('breathing', 'Breathing Exercise'),
        ('meditation', 'Meditation'),
        ('journaling', 'Journaling'),
        ('grounding', 'Grounding Technique'),
        ('progressive_relaxation', 'Progressive Muscle Relaxation'),
        ('mindfulness', 'Mindfulness'),
        ('cognitive', 'Cognitive Exercise')
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    exercise_type = models.CharField(max_length=30, choices=EXERCISE_TYPES)
    instructions = models.TextField()
    duration_minutes = models.IntegerField()
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ])
    audio_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title