from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.LandingPageView.as_view(), name='landing'),
    path('auth/login/', views.modal_login_view, name='modal_login'),
    path('auth/register/', views.modal_register_view, name='modal_register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('mood/add/', views.AddMoodEntryView.as_view(), name='add_mood'),
    path('mood/history/', views.MoodHistoryView.as_view(), name='mood_history'),
    path('mood/chart-data/', views.mood_chart_data, name='mood_chart_data'),
]