from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, MoodEntry

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'gender', 'created_at']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('birth_date', 'phone', 'gender', 'occupation', 'emergency_contact', 'emergency_phone')
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'notifications_enabled']
    list_filter = ['notifications_enabled']
    search_fields = ['user__username', 'user__email']

@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'mood', 'date']
    list_filter = ['mood', 'date']
    search_fields = ['user__username']
    ordering = ['-date']