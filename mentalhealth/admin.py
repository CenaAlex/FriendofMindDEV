from django.contrib import admin
from .models import (
    ResourceCategory, MentalHealthResource, ProfessionalContact, 
    UserResourceInteraction, SelfHelpExercise
)

@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(MentalHealthResource)
class MentalHealthResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'category', 'is_free', 'is_verified', 'is_active']
    list_filter = ['resource_type', 'category', 'is_free', 'is_verified', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['-created_at']

@admin.register(ProfessionalContact)
class ProfessionalContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialization', 'city', 'is_verified', 'is_active']
    list_filter = ['specialization', 'city', 'is_verified', 'is_active', 'accepts_insurance']
    search_fields = ['name', 'clinic_name', 'city']
    ordering = ['name']

@admin.register(SelfHelpExercise)
class SelfHelpExerciseAdmin(admin.ModelAdmin):
    list_display = ['title', 'exercise_type', 'duration_minutes', 'difficulty_level', 'is_active']
    list_filter = ['exercise_type', 'difficulty_level', 'is_active']
    search_fields = ['title', 'description']

@admin.register(UserResourceInteraction)
class UserResourceInteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'interaction_type', 'rating', 'created_at']
    list_filter = ['interaction_type', 'rating', 'created_at']
    search_fields = ['user__username']
    ordering = ['-created_at']