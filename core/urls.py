from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import admin_views
from . import feedback_views
from . import forum_views
from . import forum_admin_views
from . import mood_tracker_views
from . import mood_history_views
from . import admin_mood_analytics_views

app_name = 'core'

urlpatterns = [
    path('', views.LandingPageView.as_view(), name='landing'),
    path('auth/login/', views.modal_login_view, name='modal_login'),
    path('auth/register/', views.modal_register_view, name='modal_register'),
    path('auth/org-register/', views.modal_organization_register_view, name='modal_organization_register'),
    path('logout/', views.logout_view, name='logout'),
    path('account-suspended/', views.account_suspended_view, name='account_suspended'),
    path('request-reactivation/', views.request_reactivation_view, name='request_reactivation'),
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
    path('organization/cases/', views.OrganizationCasesView.as_view(), name='organization_cases'),
    path('organization/appointments/', views.OrganizationAppointmentsView.as_view(), name='organization_appointments'),
    path('organization/alerts/', views.OrganizationAlertsView.as_view(), name='organization_alerts'),
    path('organization/alerts/<int:alert_id>/read/', views.mark_alert_read, name='mark_alert_read'),
    path('organization/alerts/<int:alert_id>/resolve/', views.resolve_alert, name='resolve_alert'),
    
    # Admin URLs (using 'system-admin' to avoid conflicts with Django admin)
    path('system-admin/dashboard/', admin_views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('system-admin/users/', admin_views.AdminUserManagementView.as_view(), name='admin_user_management'),
    path('system-admin/users/create/', admin_views.AdminUserCreateView.as_view(), name='admin_user_create'),
    path('system-admin/users/<int:user_id>/', admin_views.AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('system-admin/users/<int:user_id>/edit/', admin_views.AdminUserEditView.as_view(), name='admin_user_edit'),
    path('system-admin/users/<int:user_id>/delete/', admin_views.admin_delete_user, name='admin_delete_user'),
    path('system-admin/users/<int:user_id>/toggle-status/', admin_views.admin_toggle_user_status, name='admin_toggle_user_status'),
    path('system-admin/organizations/', admin_views.AdminOrganizationManagementView.as_view(), name='admin_organization_management'),
    path('system-admin/organizations/create/', admin_views.AdminCreateOrganizationView.as_view(), name='admin_create_organization'),
    path('system-admin/organizations/<int:org_id>/', admin_views.AdminOrganizationDetailView.as_view(), name='admin_organization_detail'),
    path('system-admin/organizations/<int:org_id>/edit/', admin_views.AdminOrganizationEditView.as_view(), name='admin_organization_edit'),
    path('system-admin/organizations/<int:org_id>/delete/', admin_views.admin_delete_organization, name='admin_delete_organization'),
    path('system-admin/organizations/<int:org_id>/toggle-verification/', admin_views.admin_toggle_organization_verification, name='admin_toggle_organization_verification'),
    path('system-admin/organizations/quick-actions/', admin_views.admin_organization_quick_actions, name='admin_organization_quick_actions'),
    path('system-admin/analytics/', admin_views.admin_analytics_view, name='admin_analytics'),
    
    # Assessment Management URLs
    path('system-admin/assessments/', admin_views.AdminAssessmentManagementView.as_view(), name='admin_assessment_management'),
    path('system-admin/assessments/create/', admin_views.AdminAssessmentCreateView.as_view(), name='admin_assessment_create'),
    path('system-admin/assessments/<int:assessment_id>/', admin_views.AdminAssessmentDetailView.as_view(), name='admin_assessment_detail'),
    path('system-admin/assessments/<int:assessment_id>/edit/', admin_views.AdminAssessmentEditView.as_view(), name='admin_assessment_edit'),
    path('system-admin/assessments/<int:assessment_id>/delete/', admin_views.admin_delete_assessment, name='admin_delete_assessment'),
    path('system-admin/assessments/<int:assessment_id>/toggle-status/', admin_views.admin_toggle_assessment_status, name='admin_toggle_assessment_status'),
    
    # Feedback & Notification URLs
    path('feedback/submit/', feedback_views.submit_feedback, name='submit_feedback'),
    path('my-feedback/', feedback_views.my_feedback, name='my_feedback'),
    path('my-feedback/<int:feedback_id>/', feedback_views.feedback_detail, name='feedback_detail'),
    path('notifications/', feedback_views.notifications_list, name='notifications_list'),
    path('notifications/get/', feedback_views.get_notifications, name='get_notifications'),
    path('notifications/<int:notification_id>/read/', feedback_views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', feedback_views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # Admin Feedback Management
    path('system-admin/feedback/', feedback_views.AdminFeedbackManagementView.as_view(), name='admin_feedback_management'),
    path('system-admin/feedback/<int:feedback_id>/', feedback_views.AdminFeedbackDetailView.as_view(), name='admin_feedback_detail'),
    
    # Forum URLs
    path('forum/', forum_views.ForumListView.as_view(), name='forum_list'),
    path('forum/post/<int:post_id>/', forum_views.ForumPostDetailView.as_view(), name='forum_post_detail'),
    path('forum/create/', forum_views.create_post, name='forum_create_post'),
    path('forum/post/<int:post_id>/edit/', forum_views.edit_post, name='forum_edit_post'),
    path('forum/post/<int:post_id>/delete/', forum_views.delete_post, name='forum_delete_post'),
    path('forum/post/<int:post_id>/like/', forum_views.toggle_like, name='forum_toggle_like'),
    path('forum/post/<int:post_id>/comment/', forum_views.add_comment, name='forum_add_comment'),
    path('forum/comment/<int:comment_id>/edit/', forum_views.edit_comment, name='forum_edit_comment'),
    path('forum/comment/<int:comment_id>/delete/', forum_views.delete_comment, name='forum_delete_comment'),
    path('forum/post/<int:post_id>/report/', forum_views.report_post, name='forum_report_post'),
    path('forum/comment/<int:comment_id>/report/', forum_views.report_comment, name='forum_report_comment'),
    path('forum/my-posts/', forum_views.my_posts, name='forum_my_posts'),
    
    # Admin Forum Moderation
    path('system-admin/forum/', forum_admin_views.AdminForumModerationView.as_view(), name='admin_forum_moderation'),
    path('system-admin/forum/posts/', forum_admin_views.admin_all_posts, name='admin_all_posts'),
    path('system-admin/forum/reports/', forum_admin_views.AdminPostReportsView.as_view(), name='admin_post_reports'),
    path('system-admin/forum/comment-reports/', forum_admin_views.AdminCommentReportsView.as_view(), name='admin_comment_reports'),
    path('system-admin/forum/reports/<int:report_id>/', forum_admin_views.admin_review_post_report, name='admin_review_post_report'),
    path('system-admin/forum/comment-reports/<int:report_id>/', forum_admin_views.admin_review_comment_report, name='admin_review_comment_report'),
    
    # Mood Tracker Popup
    path('mood-tracker/check/', mood_tracker_views.check_mood_logged_today, name='check_mood_logged'),
    path('mood-tracker/log/', mood_tracker_views.log_mood, name='log_mood_popup'),
    path('mood-tracker/stats/', mood_tracker_views.get_mood_stats, name='mood_stats'),
    
    # Mood History & Summary
    path('mood-history/', mood_history_views.mood_history_summary, name='mood_history_summary'),
    path('mood-reasons/', mood_history_views.mood_reasons_summary, name='mood_reasons_summary'),
    
    # Admin Mood Analytics
    path('system-admin/mood-analytics/', admin_mood_analytics_views.admin_mood_analytics, name='admin_mood_analytics'),
]