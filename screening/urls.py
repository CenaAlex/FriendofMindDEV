from django.urls import path
from . import views
from . import views_enhanced

app_name = 'screening'

urlpatterns = [
    path('', views.AssessmentListView.as_view(), name='assessment_list'),
    path('history/', views.AssessmentHistoryView.as_view(), name='assessment_history'),
    path('result/<int:assessment_id>/', views.AssessmentResultView.as_view(), name='assessment_result'),
    path('<str:assessment_type>/', views.AssessmentDetailView.as_view(), name='assessment_detail'),
    
    # Enhanced one-question-at-a-time assessment
    path('<str:assessment_type>/start/', views_enhanced.start_assessment, name='start_assessment'),
    path('assessment/<int:assessment_id>/question/<int:question_number>/', views_enhanced.take_assessment_question, name='take_assessment_question'),
    
    # Redirect old take_assessment to new enhanced flow
    path('<str:assessment_type>/take/', views_enhanced.start_assessment, name='take_assessment'),
]