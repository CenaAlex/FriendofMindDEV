from django.db import models
from django.utils import timezone
from core.models import User

class Assessment(models.Model):
    ASSESSMENT_TYPES = [
        ('phq9', 'PHQ-9 (Depression)'),
        ('gad7', 'GAD-7 (Anxiety)'),
        ('pss', 'PSS (Perceived Stress Scale)')
    ]
    
    name = models.CharField(max_length=50, choices=ASSESSMENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title

class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.assessment.name} - Q{self.order}: {self.text[:50]}"

class AnswerChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    value = models.IntegerField()
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.text} ({self.value})"

class UserAssessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_score = models.IntegerField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.assessment.title}"

class UserAnswer(models.Model):
    user_assessment = models.ForeignKey(UserAssessment, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_choice = models.ForeignKey(AnswerChoice, on_delete=models.CASCADE)
    answered_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user_assessment.user.username} - Q{self.question.order}: {self.answer_choice.text}"

class AssessmentResult(models.Model):
    SEVERITY_LEVELS = [
        ('minimal', 'Minimal'),
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('moderately_severe', 'Moderately Severe'),
        ('severe', 'Severe')
    ]
    
    user_assessment = models.OneToOneField(UserAssessment, on_delete=models.CASCADE)
    severity_level = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    score_range = models.CharField(max_length=20)  # e.g., "15-19"
    recommendation = models.TextField()
    resources_suggested = models.TextField(blank=True)
    follow_up_needed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user_assessment.user.username} - {self.severity_level}"