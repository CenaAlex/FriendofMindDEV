"""
Feedback and Notification Models
Separated from main models.py for clarity
"""
from django.db import models
from django.utils import timezone
from .models import User


class Feedback(models.Model):
    """User feedback and issue reports"""
    FEEDBACK_TYPES = [
        ('feedback', 'General Feedback'),
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('issue', 'Report Issue'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_review', 'In Review'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_feedbacks')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Feedback'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_feedback_type_display()} - {self.subject[:50]}"


class FeedbackResponse(models.Model):
    """Admin responses to user feedback"""
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='responses')
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_internal_note = models.BooleanField(default=False, help_text="Internal notes are not visible to users")
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Response to {self.feedback.subject} by {self.admin_user.username}"


class Notification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPES = [
        ('feedback_response', 'Feedback Response'),
        ('feedback_status', 'Feedback Status Update'),
        ('system', 'System Notification'),
        ('assessment', 'Assessment Notification'),
        ('admin', 'Admin Notification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link_url = models.CharField(max_length=500, blank=True, help_text="Optional link to related page")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Optional: Link to related objects
    related_feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

