from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from datetime import timedelta
from .models import User, MoodEntry, Organization, OrganizationStaff, PatientCase, OrganizationAppointment, OrganizationAlert
from .forms import CustomUserCreationForm, MoodEntryForm, UserProfileForm, OrganizationRegistrationForm, OrganizationProfileForm

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
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated first (middleware might have logged them out)
        if not request.user.is_authenticated:
            return redirect('core:modal_login')
        
        # Redirect admin users to admin dashboard
        if request.user.is_superuser or request.user.is_staff:
            return redirect('core:admin_dashboard')
        elif request.user.role == 'organization':
            return redirect('core:organization_dashboard')
        return super().dispatch(request, *args, **kwargs)
    
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
        
        # Resources accessed (currently not tracked, set to 0)
        # TODO: Implement resource tracking system
        context['resources_accessed'] = 0
        
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

def account_suspended_view(request):
    """View for suspended account page"""
    return render(request, 'core/account_suspended.html')

@require_http_methods(["POST"])
def modal_login_view(request):
    """Handle login from modal form"""
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    if username and password:
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return JsonResponse({
                    'success': True, 
                    'message': 'Login successful!',
                    'redirect_url': reverse_lazy('core:dashboard')
                })
            else:
                # Account is suspended - redirect to suspended page
                return JsonResponse({
                    'success': True,  # Still "successful" but redirect to suspended page
                    'message': 'Account suspended',
                    'redirect_url': reverse_lazy('core:account_suspended')
                })
        else:
            return JsonResponse({
                'success': False, 
                'message': 'Invalid username or password.'
            })
    else:
        return JsonResponse({
            'success': False, 
            'message': 'Please fill in all fields.'
        })

@require_http_methods(["POST"])
def check_email_availability(request):
    """Check if email is available for registration"""
    import json
    data = json.loads(request.body)
    email = data.get('email', '').strip()
    
    if not email:
        return JsonResponse({'available': False, 'message': 'Email is required'})
    
    # Check if email already exists
    from .models import User
    exists = User.objects.filter(email=email).exists()
    
    return JsonResponse({
        'available': not exists,
        'message': 'Email already registered' if exists else 'Email is available'
    })

@require_http_methods(["POST"])
def modal_register_view(request):
    """Handle registration from modal form"""
    form = CustomUserCreationForm(request.POST)
    
    if form.is_valid():
        user = form.save()
        login(request, user)
        return JsonResponse({
            'success': True, 
            'message': 'Registration successful! Welcome to FriendofMind.',
            'redirect_url': reverse_lazy('core:dashboard')
        })
    else:
        # Return form errors
        errors = {}
        for field, field_errors in form.errors.items():
            errors[field] = field_errors[0] if field_errors else ''
        
        return JsonResponse({
            'success': False, 
            'message': 'Please correct the errors below.',
            'errors': errors
        })

# Enhanced Organization Views
class OrganizationCasesView(LoginRequiredMixin, TemplateView):
    template_name = 'core/organization_cases.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated first
        if not request.user.is_authenticated:
            return redirect('core:modal_login')
        
        if not request.user.role == 'organization':
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            organization = user.organization_profile
            
            # Get filter parameters
            priority_filter = self.request.GET.get('priority', '')
            status_filter = self.request.GET.get('status', '')
            staff_filter = self.request.GET.get('staff', '')
            
            # Base queryset
            cases = PatientCase.objects.filter(organization=organization, is_active=True)
            
            # Apply filters
            if priority_filter:
                cases = cases.filter(priority=priority_filter)
            if status_filter:
                cases = cases.filter(status=status_filter)
            if staff_filter:
                cases = cases.filter(assigned_staff_id=staff_filter)
            
            # Pagination
            paginator = Paginator(cases.order_by('-priority', '-created_at'), 20)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context.update({
                'organization': organization,
                'cases': page_obj,
                'priority_filter': priority_filter,
                'status_filter': status_filter,
                'staff_filter': staff_filter,
                'staff_members': OrganizationStaff.objects.filter(
                    organization=organization, is_active=True
                ),
                'priority_choices': PatientCase.PRIORITY_LEVELS,
                'status_choices': PatientCase.STATUS_CHOICES,
            })
            
        except Organization.DoesNotExist:
            context['organization'] = None
        
        return context

class OrganizationAppointmentsView(LoginRequiredMixin, TemplateView):
    template_name = 'core/organization_appointments.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated first
        if not request.user.is_authenticated:
            return redirect('core:modal_login')
        
        if not request.user.role == 'organization':
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            organization = user.organization_profile
            
            # Get filter parameters
            date_filter = self.request.GET.get('date', '')
            status_filter = self.request.GET.get('status', '')
            staff_filter = self.request.GET.get('staff', '')
            
            # Base queryset
            appointments = OrganizationAppointment.objects.filter(organization=organization)
            
            # Apply filters
            if date_filter:
                from datetime import datetime
                try:
                    filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                    appointments = appointments.filter(scheduled_date__date=filter_date)
                except ValueError:
                    pass
            if status_filter:
                appointments = appointments.filter(status=status_filter)
            if staff_filter:
                appointments = appointments.filter(staff_member_id=staff_filter)
            
            # Default to upcoming appointments if no date filter
            if not date_filter:
                appointments = appointments.filter(scheduled_date__gte=timezone.now())
            
            # Pagination
            paginator = Paginator(appointments.order_by('scheduled_date'), 20)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context.update({
                'organization': organization,
                'appointments': page_obj,
                'date_filter': date_filter,
                'status_filter': status_filter,
                'staff_filter': staff_filter,
                'staff_members': OrganizationStaff.objects.filter(
                    organization=organization, is_active=True
                ),
                'status_choices': OrganizationAppointment.STATUS_CHOICES,
                'appointment_types': OrganizationAppointment.APPOINTMENT_TYPES,
            })
            
        except Organization.DoesNotExist:
            context['organization'] = None
        
        return context

class OrganizationAlertsView(LoginRequiredMixin, TemplateView):
    template_name = 'core/organization_alerts.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated first
        if not request.user.is_authenticated:
            return redirect('core:modal_login')
        
        if not request.user.role == 'organization':
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            organization = user.organization_profile
            
            # Get filter parameters
            severity_filter = self.request.GET.get('severity', '')
            type_filter = self.request.GET.get('type', '')
            status_filter = self.request.GET.get('status', 'unread')  # Default to unread
            
            # Base queryset
            alerts = OrganizationAlert.objects.filter(organization=organization)
            
            # Apply filters
            if severity_filter:
                alerts = alerts.filter(severity=severity_filter)
            if type_filter:
                alerts = alerts.filter(alert_type=type_filter)
            if status_filter == 'unread':
                alerts = alerts.filter(is_read=False)
            elif status_filter == 'unresolved':
                alerts = alerts.filter(is_resolved=False)
            
            # Pagination
            paginator = Paginator(alerts.order_by('-created_at'), 20)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context.update({
                'organization': organization,
                'alerts': page_obj,
                'severity_filter': severity_filter,
                'type_filter': type_filter,
                'status_filter': status_filter,
                'severity_choices': OrganizationAlert.SEVERITY_LEVELS,
                'type_choices': OrganizationAlert.ALERT_TYPES,
            })
            
        except Organization.DoesNotExist:
            context['organization'] = None
        
        return context

@login_required
@require_http_methods(["POST"])
def mark_alert_read(request, alert_id):
    """Mark an alert as read"""
    # Check if user is authenticated and has organization profile
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'User not authenticated'})
    
    try:
        alert = OrganizationAlert.objects.get(
            id=alert_id, 
            organization=request.user.organization_profile
        )
        alert.is_read = True
        alert.save()
        return JsonResponse({'success': True})
    except (OrganizationAlert.DoesNotExist, Organization.DoesNotExist, AttributeError):
        return JsonResponse({'success': False, 'error': 'Alert not found'})

@login_required
@require_http_methods(["POST"])
def resolve_alert(request, alert_id):
    """Mark an alert as resolved"""
    # Check if user is authenticated and has organization profile
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'User not authenticated'})
    
    try:
        alert = OrganizationAlert.objects.get(
            id=alert_id, 
            organization=request.user.organization_profile
        )
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save()
        return JsonResponse({'success': True})
    except (OrganizationAlert.DoesNotExist, Organization.DoesNotExist, AttributeError):
        return JsonResponse({'success': False, 'error': 'Alert not found'})

# Organization Views
class OrganizationDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/organization_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated first
        if not request.user.is_authenticated:
            return redirect('core:modal_login')
        
        if not request.user.role == 'organization':
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            organization = user.organization_profile
            context['organization'] = organization
        except Organization.DoesNotExist:
            context['organization'] = None
            return context
        
        # Get organization statistics
        from screening.models import UserAssessment, AssessmentResult
        
        # Get all users who have taken assessments
        all_assessments = UserAssessment.objects.filter(is_completed=True)
        context['total_assessments'] = all_assessments.count()
        
        # Get recent assessments (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_assessments = all_assessments.filter(completed_at__gte=thirty_days_ago)
        context['recent_assessments'] = recent_assessments.count()
        
        # Get assessment results that need attention
        severe_results = AssessmentResult.objects.filter(
            severity_level__in=['moderately_severe', 'severe']
        ).order_by('-created_at')[:10]
        context['severe_cases'] = severe_results
        
        # Get organization staff
        context['staff_count'] = OrganizationStaff.objects.filter(
            organization=organization, is_active=True
        ).count()
        
        # Get mood data for insights
        recent_moods = MoodEntry.objects.filter(
            date__gte=thirty_days_ago
        ).order_by('-date')[:50]
        context['recent_moods'] = recent_moods
        
        # New enhanced features
        # Patient cases
        context['active_cases'] = PatientCase.objects.filter(
            organization=organization, is_active=True
        ).count()
        
        context['urgent_cases'] = PatientCase.objects.filter(
            organization=organization, 
            priority='urgent', 
            is_active=True
        ).order_by('-created_at')[:5]
        
        context['high_priority_cases'] = PatientCase.objects.filter(
            organization=organization, 
            priority='high', 
            is_active=True
        ).order_by('-created_at')[:5]
        
        # Today's appointments
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        context['todays_appointments'] = OrganizationAppointment.objects.filter(
            organization=organization,
            scheduled_date__date=today,
            status__in=['scheduled', 'confirmed']
        ).order_by('scheduled_date')[:10]
        
        context['tomorrows_appointments'] = OrganizationAppointment.objects.filter(
            organization=organization,
            scheduled_date__date=tomorrow,
            status__in=['scheduled', 'confirmed']
        ).order_by('scheduled_date')[:5]
        
        # Alerts
        context['unread_alerts'] = OrganizationAlert.objects.filter(
            organization=organization, 
            is_read=False
        ).order_by('-created_at')[:10]
        
        context['critical_alerts'] = OrganizationAlert.objects.filter(
            organization=organization, 
            severity='critical',
            is_resolved=False
        ).count()
        
        # Weekly statistics
        week_ago = timezone.now() - timedelta(days=7)
        context['weekly_appointments'] = OrganizationAppointment.objects.filter(
            organization=organization,
            scheduled_date__gte=week_ago,
            status='completed'
        ).count()
        
        context['missed_appointments'] = OrganizationAppointment.objects.filter(
            organization=organization,
            scheduled_date__gte=week_ago,
            status='no_show'
        ).count()
        
        # Follow-up due
        context['followups_due'] = PatientCase.objects.filter(
            organization=organization,
            next_followup_date__lte=timezone.now(),
            is_active=True
        ).count()
        
        return context

class OrganizationProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'core/organization_profile.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated first
        if not request.user.is_authenticated:
            return redirect('core:modal_login')
        
        if not request.user.role == 'organization':
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            organization = user.organization_profile
            context['form'] = OrganizationProfileForm(instance=organization)
        except Organization.DoesNotExist:
            context['form'] = OrganizationProfileForm()
            context['organization'] = None
        
        return context
    
    def post(self, request, *args, **kwargs):
        user = request.user
        
        try:
            organization = user.organization_profile
            form = OrganizationProfileForm(request.POST, instance=organization)
        except Organization.DoesNotExist:
            form = OrganizationProfileForm(request.POST)
        
        if form.is_valid():
            organization = form.save(commit=False)
            organization.user = user
            organization.save()
            messages.success(request, 'Organization profile updated successfully!')
            return redirect('core:organization_profile')
        
        return self.render_to_response({'form': form})

class OrganizationRegistrationView(CreateView):
    form_class = OrganizationRegistrationForm
    template_name = 'core/organization_register.html'
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Organization registration successful! Please complete your organization profile.')
        return redirect('core:organization_profile')

class OrganizationStaffView(LoginRequiredMixin, TemplateView):
    template_name = 'core/organization_staff.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated first
        if not request.user.is_authenticated:
            return redirect('core:modal_login')
        
        if not request.user.role == 'organization':
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            organization = user.organization_profile
            context['staff'] = OrganizationStaff.objects.filter(
                organization=organization, is_active=True
            ).order_by('-joined_at')
            context['organization'] = organization
        except Organization.DoesNotExist:
            context['staff'] = []
            context['organization'] = None
        
        return context

class OrganizationAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'core/organization_analytics.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated first
        if not request.user.is_authenticated:
            return redirect('core:modal_login')
        
        if not request.user.role == 'organization':
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from screening.models import UserAssessment, AssessmentResult
        
        # Get assessment analytics
        all_assessments = UserAssessment.objects.filter(is_completed=True)
        
        # Monthly assessment trends
        monthly_data = {}
        for i in range(12):
            month_start = timezone.now() - timedelta(days=30*i)
            month_end = timezone.now() - timedelta(days=30*(i-1)) if i > 0 else timezone.now()
            count = all_assessments.filter(
                completed_at__gte=month_start,
                completed_at__lt=month_end
            ).count()
            monthly_data[month_start.strftime('%Y-%m')] = count
        
        context['monthly_assessments'] = monthly_data
        
        # Assessment type distribution
        assessment_types = {}
        for assessment in all_assessments:
            name = assessment.assessment.name
            assessment_types[name] = assessment_types.get(name, 0) + 1
        
        context['assessment_types'] = assessment_types
        
        # Severity level distribution
        severity_levels = {}
        results = AssessmentResult.objects.filter(
            user_assessment__is_completed=True
        )
        for result in results:
            level = result.severity_level
            severity_levels[level] = severity_levels.get(level, 0) + 1
        
        context['severity_levels'] = severity_levels
        
        return context

@require_http_methods(["POST"])
def modal_organization_register_view(request):
    """Handle organization registration from modal form"""
    form = OrganizationRegistrationForm(request.POST)
    
    if form.is_valid():
        user = form.save()
        login(request, user)
        return JsonResponse({
            'success': True, 
            'message': 'Organization registration successful! Please complete your organization profile.',
            'redirect_url': reverse_lazy('core:organization_profile')
        })
    else:
        # Return form errors
        errors = {}
        for field, field_errors in form.errors.items():
            errors[field] = field_errors[0] if field_errors else ''
        
        return JsonResponse({
            'success': False, 
            'message': 'Please correct the errors below.',
            'errors': errors
        })

# Enhanced Organization Views
class OrganizationCasesView(LoginRequiredMixin, TemplateView):
    template_name = 'core/organization_cases.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated first
        if not request.user.is_authenticated:
            return redirect('core:modal_login')
        
        if not request.user.role == 'organization':
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            organization = user.organization_profile
            
            # Get filter parameters
            priority_filter = self.request.GET.get('priority', '')
            status_filter = self.request.GET.get('status', '')
            staff_filter = self.request.GET.get('staff', '')
            
            # Base queryset
            cases = PatientCase.objects.filter(organization=organization, is_active=True)
            
            # Apply filters
            if priority_filter:
                cases = cases.filter(priority=priority_filter)
            if status_filter:
                cases = cases.filter(status=status_filter)
            if staff_filter:
                cases = cases.filter(assigned_staff_id=staff_filter)
            
            # Pagination
            paginator = Paginator(cases.order_by('-priority', '-created_at'), 20)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context.update({
                'organization': organization,
                'cases': page_obj,
                'priority_filter': priority_filter,
                'status_filter': status_filter,
                'staff_filter': staff_filter,
                'staff_members': OrganizationStaff.objects.filter(
                    organization=organization, is_active=True
                ),
                'priority_choices': PatientCase.PRIORITY_LEVELS,
                'status_choices': PatientCase.STATUS_CHOICES,
            })
            
        except Organization.DoesNotExist:
            context['organization'] = None
        
        return context

class OrganizationAppointmentsView(LoginRequiredMixin, TemplateView):
    template_name = 'core/organization_appointments.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated first
        if not request.user.is_authenticated:
            return redirect('core:modal_login')
        
        if not request.user.role == 'organization':
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            organization = user.organization_profile
            
            # Get filter parameters
            date_filter = self.request.GET.get('date', '')
            status_filter = self.request.GET.get('status', '')
            staff_filter = self.request.GET.get('staff', '')
            
            # Base queryset
            appointments = OrganizationAppointment.objects.filter(organization=organization)
            
            # Apply filters
            if date_filter:
                from datetime import datetime
                try:
                    filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                    appointments = appointments.filter(scheduled_date__date=filter_date)
                except ValueError:
                    pass
            if status_filter:
                appointments = appointments.filter(status=status_filter)
            if staff_filter:
                appointments = appointments.filter(staff_member_id=staff_filter)
            
            # Default to upcoming appointments if no date filter
            if not date_filter:
                appointments = appointments.filter(scheduled_date__gte=timezone.now())
            
            # Pagination
            paginator = Paginator(appointments.order_by('scheduled_date'), 20)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context.update({
                'organization': organization,
                'appointments': page_obj,
                'date_filter': date_filter,
                'status_filter': status_filter,
                'staff_filter': staff_filter,
                'staff_members': OrganizationStaff.objects.filter(
                    organization=organization, is_active=True
                ),
                'status_choices': OrganizationAppointment.STATUS_CHOICES,
                'appointment_types': OrganizationAppointment.APPOINTMENT_TYPES,
            })
            
        except Organization.DoesNotExist:
            context['organization'] = None
        
        return context

class OrganizationAlertsView(LoginRequiredMixin, TemplateView):
    template_name = 'core/organization_alerts.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated first
        if not request.user.is_authenticated:
            return redirect('core:modal_login')
        
        if not request.user.role == 'organization':
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            organization = user.organization_profile
            
            # Get filter parameters
            severity_filter = self.request.GET.get('severity', '')
            type_filter = self.request.GET.get('type', '')
            status_filter = self.request.GET.get('status', 'unread')  # Default to unread
            
            # Base queryset
            alerts = OrganizationAlert.objects.filter(organization=organization)
            
            # Apply filters
            if severity_filter:
                alerts = alerts.filter(severity=severity_filter)
            if type_filter:
                alerts = alerts.filter(alert_type=type_filter)
            if status_filter == 'unread':
                alerts = alerts.filter(is_read=False)
            elif status_filter == 'unresolved':
                alerts = alerts.filter(is_resolved=False)
            
            # Pagination
            paginator = Paginator(alerts.order_by('-created_at'), 20)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context.update({
                'organization': organization,
                'alerts': page_obj,
                'severity_filter': severity_filter,
                'type_filter': type_filter,
                'status_filter': status_filter,
                'severity_choices': OrganizationAlert.SEVERITY_LEVELS,
                'type_choices': OrganizationAlert.ALERT_TYPES,
            })
            
        except Organization.DoesNotExist:
            context['organization'] = None
        
        return context

@login_required
@require_http_methods(["POST"])
def mark_alert_read(request, alert_id):
    """Mark an alert as read"""
    # Check if user is authenticated and has organization profile
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'User not authenticated'})
    
    try:
        alert = OrganizationAlert.objects.get(
            id=alert_id, 
            organization=request.user.organization_profile
        )
        alert.is_read = True
        alert.save()
        return JsonResponse({'success': True})
    except (OrganizationAlert.DoesNotExist, Organization.DoesNotExist, AttributeError):
        return JsonResponse({'success': False, 'error': 'Alert not found'})

@login_required
@require_http_methods(["POST"])
def resolve_alert(request, alert_id):
    """Mark an alert as resolved"""
    # Check if user is authenticated and has organization profile
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'User not authenticated'})
    
    try:
        alert = OrganizationAlert.objects.get(
            id=alert_id, 
            organization=request.user.organization_profile
        )
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save()
        return JsonResponse({'success': True})
    except (OrganizationAlert.DoesNotExist, Organization.DoesNotExist, AttributeError):
        return JsonResponse({'success': False, 'error': 'Alert not found'})