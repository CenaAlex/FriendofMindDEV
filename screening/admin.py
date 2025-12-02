from django.contrib import admin
from .models import Assessment, Question, AnswerChoice, UserAssessment, UserAnswer, AssessmentResult

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0

class AnswerChoiceInline(admin.TabularInline):
    model = AnswerChoice
    extra = 0

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'is_active', 'created_at']
    list_filter = ['name', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['assessment', 'text', 'order']
    list_filter = ['assessment']
    search_fields = ['text']
    inlines = [AnswerChoiceInline]

@admin.register(UserAssessment)
class UserAssessmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'assessment', 'total_score', 'is_completed', 'started_at']
    list_filter = ['assessment', 'is_completed', 'started_at']
    search_fields = ['user__username']
    ordering = ['-started_at']

@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ['user_assessment', 'severity_level', 'score_range', 'follow_up_needed']
    list_filter = ['severity_level', 'follow_up_needed']
    search_fields = ['user_assessment__user__username']