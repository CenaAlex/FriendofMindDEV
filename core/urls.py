from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import admin_views

app_name = 'core'

urlpatterns = [
    path('', views.LandingPageView.as_view(), name='landing'),
    path('auth/login/', views.modal_login_view, name='modal_login'),
    path('auth/register/', views.modal_register_view, name='modal_register'),
    path('auth/org-register/', views.modal_organization_register_view, name='modal_organization_register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('mood/add/', views.AddMoodEntryView.as_view(), name='add_mood'),
    path('mood/history/', views.MoodHistoryView.as_view(), name='mood_history'),
    path('mood/chart-data/', views.mood_chart_data, name='mood_chart_data'),
    
    # Organization URLs
    path('organization/register/', views.OrganizationRegistrationView.as_view(), name='organization_register'),
    path('organization/dashboard/', views.OrganizationDashboardView.as_view(), name='organization_dashboard'),
    path('organization/profile/', views.OrganizationProfileView.as_view(), name='organization_profile'),
    path('organization/staff/', views.OrganizationStaffView.as_view(), name='organization_staff'),
    path('organization/analytics/', views.OrganizationAnalyticsView.as_view(), name='organization_analytics'),
    
    # Admin URLs (using 'system-admin' to avoid conflicts with Django admin)
    path('system-admin/dashboard/', admin_views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('system-admin/users/', admin_views.AdminUserManagementView.as_view(), name='admin_user_management'),
    path('system-admin/users/<int:user_id>/', admin_views.AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('system-admin/organizations/', admin_views.AdminOrganizationManagementView.as_view(), name='admin_organization_management'),
    path('system-admin/organizations/<int:org_id>/', admin_views.AdminOrganizationDetailView.as_view(), name='admin_organization_detail'),
    path('system-admin/analytics/', admin_views.admin_analytics_view, name='admin_analytics'),
    path('system-admin/users/<int:user_id>/toggle-status/', admin_views.admin_toggle_user_status, name='admin_toggle_user_status'),
    path('system-admin/organizations/<int:org_id>/toggle-verification/', admin_views.admin_toggle_organization_verification, name='admin_toggle_organization_verification'),
]