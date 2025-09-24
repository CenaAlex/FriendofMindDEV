from django.urls import path
from . import views

app_name = 'mentalhealth'

urlpatterns = [
    path('', views.ResourceListView.as_view(), name='resource_list'),
    path('category/<int:category_id>/', views.ResourceByCategoryView.as_view(), name='resource_by_category'),
    path('professionals/', views.ProfessionalListView.as_view(), name='professional_list'),
    path('exercises/', views.SelfHelpExerciseListView.as_view(), name='exercise_list'),
    path('exercise/<int:exercise_id>/', views.ExerciseDetailView.as_view(), name='exercise_detail'),
    path('contact/<int:contact_id>/', views.ProfessionalDetailView.as_view(), name='professional_detail'),
]