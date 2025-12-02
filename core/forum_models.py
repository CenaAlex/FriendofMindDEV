"""
Forum/Community Models
Social interaction system for users
"""
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from .models import User


class ForumPost(models.Model):
    """User forum posts - text or images"""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    content = models.TextField(blank=True, help_text="Post text content")
    image = models.ImageField(
        upload_to='forum_images/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])],
        help_text="Optional image attachment"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False, help_text="Post has been reported")
    is_hidden = models.BooleanField(default=False, help_text="Hidden by admin")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author']),
            models.Index(fields=['is_flagged']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] if self.content else "[Image Post]"
        return f"{self.author.username} - {content_preview}"
    
    def like_count(self):
        return self.likes.count()
    
    def comment_count(self):
        return self.comments.filter(is_hidden=False).count()
    
    def report_count(self):
        return self.reports.count()
    
    def is_liked_by(self, user):
        if not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()
    
    def can_edit(self, user):
        """Check if user can edit this post"""
        return self.author == user
    
    def can_delete(self, user):
        """Check if user can delete this post"""
        return self.author == user or user.is_superuser or user.is_staff


class ForumComment(models.Model):
    """Comments on forum posts"""
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_comments')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False, help_text="Comment has been reported")
    is_hidden = models.BooleanField(default=False, help_text="Hidden by admin")
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['author']),
            models.Index(fields=['is_flagged']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50]
        return f"{self.author.username} on {self.post.id} - {content_preview}"
    
    def report_count(self):
        return self.comment_reports.count()
    
    def can_edit(self, user):
        """Check if user can edit this comment"""
        return self.author == user
    
    def can_delete(self, user):
        """Check if user can delete this comment"""
        return self.author == user or user.is_superuser or user.is_staff


class ForumLike(models.Model):
    """Likes/Hearts on forum posts"""
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_likes')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['post', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', 'user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} likes post {self.post.id}"


class ForumReport(models.Model):
    """Reports for inappropriate posts"""
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment or Bullying'),
        ('hate_speech', 'Hate Speech'),
        ('violence', 'Violence or Threats'),
        ('inappropriate', 'Inappropriate Content'),
        ('misinformation', 'Misinformation'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('action_taken', 'Action Taken'),
        ('dismissed', 'Dismissed'),
    ]
    
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_reports')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True, help_text="Additional details about the report")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports')
    admin_notes = models.TextField(blank=True, help_text="Internal admin notes")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['post']),
        ]
    
    def __str__(self):
        return f"Report by {self.reporter.username} - {self.get_reason_display()}"


class ForumCommentReport(models.Model):
    """Reports for inappropriate comments"""
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment or Bullying'),
        ('hate_speech', 'Hate Speech'),
        ('violence', 'Violence or Threats'),
        ('inappropriate', 'Inappropriate Content'),
        ('misinformation', 'Misinformation'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('action_taken', 'Action Taken'),
        ('dismissed', 'Dismissed'),
    ]
    
    comment = models.ForeignKey(ForumComment, on_delete=models.CASCADE, related_name='comment_reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_reports_made')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True, help_text="Additional details about the report")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_comment_reports')
    admin_notes = models.TextField(blank=True, help_text="Internal admin notes")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['comment']),
        ]
    
    def __str__(self):
        return f"Comment Report by {self.reporter.username} - {self.get_reason_display()}"

