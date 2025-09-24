from django.urls import path
from . import views

app_name = 'screening'

urlpatterns = [
    path('', views.AssessmentListView.as_view(), name='assessment_list'),
    path('history/', views.AssessmentHistoryView.as_view(), name='assessment_history'),
    path('result/<int:assessment_id>/', views.AssessmentResultView.as_view(), name='assessment_result'),
    path('<str:assessment_type>/', views.AssessmentDetailView.as_view(), name='assessment_detail'),
    path('<str:assessment_type>/take/', views.TakeAssessmentView.as_view(), name='take_assessment'),
]