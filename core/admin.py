from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, MoodEntry, Organization, OrganizationStaff, PatientCase, OrganizationAppointment, OrganizationAlert

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'created_at']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active', 'gender', 'created_at']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-created_at']
    list_editable = ['is_active']
    actions = ['make_organization_users', 'make_regular_users', 'activate_users', 'deactivate_users']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'birth_date', 'phone', 'gender', 'occupation', 'emergency_contact', 'emergency_phone')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'first_name', 'last_name', 'role', 'phone')
        }),
    )
    
    def make_organization_users(self, request, queryset):
        """Bulk action to convert users to organization role"""
        updated = queryset.update(role='organization')
        self.message_user(request, f'{updated} users were converted to organization accounts.')
    make_organization_users.short_description = "Convert selected users to organization accounts"
    
    def make_regular_users(self, request, queryset):
        """Bulk action to convert users to regular role"""
        updated = queryset.update(role='user')
        self.message_user(request, f'{updated} users were converted to regular user accounts.')
    make_regular_users.short_description = "Convert selected users to regular user accounts"
    
    def activate_users(self, request, queryset):
        """Bulk action to activate users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user accounts were activated.')
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        """Bulk action to deactivate users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user accounts were deactivated.')
    deactivate_users.short_description = "Deactivate selected users"

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

class OrganizationUserInline(admin.StackedInline):
    """Inline to create user account when creating organization"""
    model = User
    fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_active')
    extra = 0
    max_num = 1
    can_delete = False

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['organization_name', 'organization_type', 'city', 'state', 'is_verified', 'user_active', 'created_at']
    list_filter = ['organization_type', 'is_verified', 'emergency_services', 'created_at', 'user__is_active']
    search_fields = ['organization_name', 'city', 'state', 'email', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_verified']
    actions = ['verify_organizations', 'unverify_organizations', 'activate_users', 'deactivate_users']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'organization_name', 'organization_type', 'license_number')
        }),
        ('Contact Information', {
            'fields': ('address', 'city', 'state', 'zip_code', 'country', 'phone', 'email', 'website')
        }),
        ('Services', {
            'fields': ('description', 'services_offered', 'operating_hours', 'emergency_services', 
                      'insurance_accepted', 'languages_spoken')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_documents')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_active(self, obj):
        """Show if the associated user account is active"""
        return obj.user.is_active
    user_active.boolean = True
    user_active.short_description = 'User Active'
    
    def verify_organizations(self, request, queryset):
        """Bulk action to verify organizations"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} organizations were verified.')
    verify_organizations.short_description = "Verify selected organizations"
    
    def unverify_organizations(self, request, queryset):
        """Bulk action to unverify organizations"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} organizations were unverified.')
    unverify_organizations.short_description = "Unverify selected organizations"
    
    def activate_users(self, request, queryset):
        """Bulk action to activate user accounts"""
        user_ids = [org.user.id for org in queryset]
        updated = User.objects.filter(id__in=user_ids).update(is_active=True)
        self.message_user(request, f'{updated} user accounts were activated.')
    activate_users.short_description = "Activate user accounts for selected organizations"
    
    def deactivate_users(self, request, queryset):
        """Bulk action to deactivate user accounts"""
        user_ids = [org.user.id for org in queryset]
        updated = User.objects.filter(id__in=user_ids).update(is_active=False)
        self.message_user(request, f'{updated} user accounts were deactivated.')
    deactivate_users.short_description = "Deactivate user accounts for selected organizations"

@admin.register(OrganizationStaff)
class OrganizationStaffAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'organization__organization_name']
    date_hierarchy = 'joined_at'

@admin.register(PatientCase)
class PatientCaseAdmin(admin.ModelAdmin):
    list_display = ['case_number', 'patient_user', 'organization', 'priority', 'status', 'assigned_staff', 'created_at']
    list_filter = ['priority', 'status', 'is_active', 'created_at', 'organization']
    search_fields = ['case_number', 'patient_user__username', 'patient_user__first_name', 'patient_user__last_name']
    readonly_fields = ['case_number', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

@admin.register(OrganizationAppointment)
class OrganizationAppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient_user', 'staff_member', 'appointment_type', 'scheduled_date', 'status', 'is_online']
    list_filter = ['appointment_type', 'status', 'is_online', 'scheduled_date', 'organization']
    search_fields = ['patient_user__username', 'staff_member__user__username', 'notes']
    date_hierarchy = 'scheduled_date'

@admin.register(OrganizationAlert)
class OrganizationAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization', 'alert_type', 'severity', 'is_read', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'severity', 'is_read', 'is_resolved', 'created_at', 'organization']
    search_fields = ['title', 'message', 'related_user__username']
    readonly_fields = ['created_at', 'resolved_at']
    date_hierarchy = 'created_at'