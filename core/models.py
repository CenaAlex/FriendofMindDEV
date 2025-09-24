from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=20, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ], blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=15, blank=True)
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