from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib import messages
from django.db.models import Count, Avg
from django.utils import timezone
from django.urls import reverse_lazy
from django.http import JsonResponse
from datetime import timedelta
from .models import User, MoodEntry
from .forms import CustomUserCreationForm, MoodEntryForm, UserProfileForm

class LandingPageView(TemplateView):
    template_name = 'core/landing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = User.objects.count()
        context['assessments_completed'] = 0  # Will be updated with actual data
        return context

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'core/register.html'
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Registration successful! Welcome to FriendofMind.')
        return redirect('core:dashboard')

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        from screening.models import UserAssessment, AssessmentResult
        
        context['recent_moods'] = MoodEntry.objects.filter(user=user)[:7]
        
        week_ago = timezone.now() - timedelta(days=7)
        context['mood_avg_week'] = MoodEntry.objects.filter(
            user=user, date__gte=week_ago
        ).aggregate(avg_mood=Avg('mood'))['avg_mood'] or 0
        
        completed_assessments = UserAssessment.objects.filter(user=user, is_completed=True)
        context['assessments_taken'] = completed_assessments.count()
        context['recent_assessment'] = completed_assessments.first()
        
        context['phq9_count'] = completed_assessments.filter(assessment__name='phq9').count()
        context['gad7_count'] = completed_assessments.filter(assessment__name='gad7').count()
        context['pss_count'] = completed_assessments.filter(assessment__name='pss').count()
        
        latest_results = AssessmentResult.objects.filter(
            user_assessment__user=user,
            user_assessment__is_completed=True
        ).order_by('-created_at')[:3]
        
        context['latest_results'] = latest_results
        context['needs_attention'] = any(
            result.severity_level in ['moderately_severe', 'severe'] 
            for result in latest_results
        )
        
        return context

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'core/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserProfileForm(instance=self.request.user)
        return context
    
    def post(self, request, *args, **kwargs):
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('core:profile')
        return self.render_to_response({'form': form})

class AddMoodEntryView(LoginRequiredMixin, CreateView):
    model = MoodEntry
    form_class = MoodEntryForm
    template_name = 'core/add_mood.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Mood entry added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('core:mood_history')
    
    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            mood_value = request.POST.get('mood')
            notes = request.POST.get('notes', '')
            
            if mood_value:
                try:
                    MoodEntry.objects.create(
                        user=request.user,
                        mood=int(mood_value),
                        notes=notes
                    )
                    return JsonResponse({'success': True})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})
            else:
                return JsonResponse({'success': False, 'error': 'Mood value is required'})
        
        return super().post(request, *args, **kwargs)

@login_required
def mood_chart_data(request):
    user = request.user
    
    week_ago = timezone.now() - timedelta(days=7)
    moods = MoodEntry.objects.filter(
        user=user,
        date__gte=week_ago
    ).order_by('date').values('mood', 'date')
    
    mood_data = []
    for mood in moods:
        mood_data.append({
            'mood': mood['mood'],
            'date': mood['date'].strftime('%Y-%m-%d')
        })
    
    return JsonResponse({'moods': mood_data})

class MoodHistoryView(LoginRequiredMixin, ListView):
    model = MoodEntry
    template_name = 'core/mood_history.html'
    context_object_name = 'mood_entries'
    paginate_by = 20
    
    def get_queryset(self):
        return MoodEntry.objects.filter(user=self.request.user)

def logout_view(request):
    logout(request)
    return redirect('core:landing')