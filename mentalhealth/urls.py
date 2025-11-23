from django.urls import path
from . import views
from . import resource_enhanced_views as enhanced

app_name = 'mentalhealth'

urlpatterns = [
    # Public/User Resource Views
    path('', views.ResourceListView.as_view(), name='resource_list'),
    path('category/<int:category_id>/', views.ResourceByCategoryView.as_view(), name='resource_by_category'),
    path('resource/<int:resource_id>/', enhanced.ResourceDetailView.as_view(), name='resource_detail'),
    
    # Bookmarking
    path('bookmark/<int:resource_id>/', enhanced.bookmark_resource, name='bookmark_resource'),
    path('my-bookmarks/', enhanced.my_bookmarks, name='my_bookmarks'),
    
    # Reporting
    path('report/<int:resource_id>/', enhanced.report_resource, name='report_resource'),
    
    # Professionals & Exercises
    path('professionals/', views.ProfessionalListView.as_view(), name='professional_list'),
    path('contact/<int:contact_id>/', views.ProfessionalDetailView.as_view(), name='professional_detail'),
    path('exercises/', views.SelfHelpExerciseListView.as_view(), name='exercise_list'),
    path('exercise/<int:exercise_id>/', views.ExerciseDetailView.as_view(), name='exercise_detail'),
    
    # Admin Resource Management
    path('admin/resources/', enhanced.AdminResourceListView.as_view(), name='admin_resource_list'),
    path('admin/resource/create/', enhanced.AdminResourceCreateView.as_view(), name='admin_resource_create'),
    path('admin/resource/<int:resource_id>/edit/', enhanced.AdminResourceUpdateView.as_view(), name='admin_resource_edit'),
    path('admin/resource/<int:resource_id>/delete/', enhanced.admin_delete_resource, name='admin_resource_delete'),
    path('admin/resource/<int:resource_id>/toggle/', enhanced.admin_toggle_resource_status, name='admin_resource_toggle'),
]