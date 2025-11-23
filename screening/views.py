from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Assessment, UserAssessment, Question, AnswerChoice, UserAnswer, AssessmentResult

class AssessmentListView(LoginRequiredMixin, ListView):
    model = Assessment
    template_name = 'screening/assessment_list.html'
    context_object_name = 'assessments'
    
    def dispatch(self, request, *args, **kwargs):
        # Block admins and staff from taking assessments
        if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
            messages.warning(request, 'Admins cannot take assessments. Please use the Assessment Management dashboard.')
            return redirect('core:admin_dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Assessment.objects.filter(is_active=True)

class AssessmentDetailView(LoginRequiredMixin, DetailView):
    model = Assessment
    template_name = 'screening/assessment_detail.html'
    slug_field = 'name'
    slug_url_kwarg = 'assessment_type'

class TakeAssessmentView(LoginRequiredMixin, TemplateView):
    template_name = 'screening/take_assessment.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Block admins and staff from taking assessments
        if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
            messages.warning(request, 'Admins cannot take assessments. You can manage assessments from the admin panel.')
            return redirect('core:admin_dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assessment_type = kwargs.get('assessment_type')
        context['assessment'] = get_object_or_404(Assessment, name=assessment_type)
        context['questions'] = context['assessment'].questions.all()
        return context
    
    def post(self, request, *args, **kwargs):
        assessment_type = kwargs.get('assessment_type')
        assessment = get_object_or_404(Assessment, name=assessment_type)
        
        # Create user assessment
        user_assessment = UserAssessment.objects.create(
            user=request.user,
            assessment=assessment
        )
        
        total_score = 0
        
        # Process answers
        for question in assessment.questions.all():
            answer_id = request.POST.get(f'question_{question.id}')
            if answer_id:
                answer_choice = get_object_or_404(AnswerChoice, id=answer_id)
                UserAnswer.objects.create(
                    user_assessment=user_assessment,
                    question=question,
                    answer_choice=answer_choice
                )
                total_score += answer_choice.value
        
        # Complete assessment
        user_assessment.total_score = total_score
        user_assessment.is_completed = True
        user_assessment.save()
        
        # Create result (simplified logic)
        severity_level = self.calculate_severity(assessment.name, total_score)
        AssessmentResult.objects.create(
            user_assessment=user_assessment,
            severity_level=severity_level,
            score_range=f"{total_score}",
            recommendation=self.get_recommendation(severity_level)
        )
        
        messages.success(request, 'Assessment completed successfully!')
        return redirect('screening:assessment_result', assessment_id=user_assessment.id)
    
    def calculate_severity(self, assessment_name, score):
        if assessment_name == 'phq9':
            if score < 5: return 'minimal'
            elif score < 10: return 'mild'
            elif score < 15: return 'moderate'
            elif score < 20: return 'moderately_severe'
            else: return 'severe'
        elif assessment_name == 'gad7':
            if score < 5: return 'minimal'
            elif score < 10: return 'mild'
            elif score < 15: return 'moderate'
            else: return 'severe'
        else:  # PSS
            if score < 13: return 'minimal'
            elif score < 20: return 'mild'
            elif score < 27: return 'moderate'
            else: return 'severe'
    
    def get_recommendation(self, severity_level):
        recommendations = {
            'minimal': 'Your scores suggest minimal symptoms. Continue with self-care practices.',
            'mild': 'Consider speaking with a mental health professional and explore self-help resources.',
            'moderate': 'We recommend consulting with a mental health professional for further evaluation.',
            'moderately_severe': 'Please consider seeking professional help soon. Your symptoms may benefit from treatment.',
            'severe': 'We strongly recommend seeking immediate professional help. Please consider contacting a mental health provider or crisis line.'
        }
        return recommendations.get(severity_level, 'Please consult with a mental health professional.')

class AssessmentResultView(LoginRequiredMixin, DetailView):
    model = UserAssessment
    template_name = 'screening/assessment_result.html'
    pk_url_kwarg = 'assessment_id'
    context_object_name = 'user_assessment'

class AssessmentHistoryView(LoginRequiredMixin, ListView):
    model = UserAssessment
    template_name = 'screening/assessment_history.html'
    context_object_name = 'assessments'
    paginate_by = 10
    
    def dispatch(self, request, *args, **kwargs):
        # Block admins and staff from viewing assessment history (they have no assessments)
        if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
            messages.info(request, 'Admins do not have assessment history. Please use Assessment Management.')
            return redirect('core:admin_dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return UserAssessment.objects.filter(
            user=self.request.user, 
            is_completed=True
        ).select_related('assessment', 'assessmentresult').order_by('-completed_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Assessment type breakdown
        assessments = self.get_queryset()
        context['phq9_assessments'] = assessments.filter(assessment__name='phq9')
        context['gad7_assessments'] = assessments.filter(assessment__name='gad7')
        context['pss_assessments'] = assessments.filter(assessment__name='pss')
        
        # Latest scores by type for trends
        context['latest_phq9'] = context['phq9_assessments'].first()
        context['latest_gad7'] = context['gad7_assessments'].first()
        context['latest_pss'] = context['pss_assessments'].first()
        
        # Calculate improvement trends (simplified)
        if context['phq9_assessments'].count() >= 2:
            latest_phq9 = context['phq9_assessments'][0]
            previous_phq9 = context['phq9_assessments'][1]
            context['phq9_trend'] = 'improving' if latest_phq9.total_score < previous_phq9.total_score else 'stable'
        
        if context['gad7_assessments'].count() >= 2:
            latest_gad7 = context['gad7_assessments'][0]
            previous_gad7 = context['gad7_assessments'][1]
            context['gad7_trend'] = 'improving' if latest_gad7.total_score < previous_gad7.total_score else 'stable'
            
        if context['pss_assessments'].count() >= 2:
            latest_pss = context['pss_assessments'][0]
            previous_pss = context['pss_assessments'][1]
            context['pss_trend'] = 'improving' if latest_pss.total_score < previous_pss.total_score else 'stable'
        
        return context