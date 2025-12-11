from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from datetime import timedelta
from .models import User, MoodEntry, Organization, OrganizationStaff
from .forms import AdminOrganizationCreationForm, AdminUserEditForm, AdminUserCreateForm, AdminOrganizationEditForm
from screening.models import Assessment, Question, AnswerChoice, UserAssessment
from screening.forms import AssessmentForm, QuestionForm, AnswerChoiceForm

def is_admin(user):
    """Check if user is admin (superuser or staff)"""
    return user.is_superuser or user.is_staff

class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to require admin access"""
    def test_func(self):
        return is_admin(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access this page.')
        return redirect('core:dashboard')

class AdminDashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'core/admin_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # User statistics
        context['total_users'] = User.objects.count()
        context['regular_users'] = User.objects.filter(role='user').count()
        context['organizations'] = User.objects.filter(role='organization').count()
        context['verified_organizations'] = Organization.objects.filter(is_verified=True).count()
        context['unverified_organizations'] = Organization.objects.filter(is_verified=False).count()
        
        # Recent registrations (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        context['recent_users'] = User.objects.filter(created_at__gte=thirty_days_ago).count()
        
        # Assessment statistics
        from screening.models import UserAssessment, AssessmentResult
        
        context['total_assessments'] = UserAssessment.objects.filter(is_completed=True).count()
        context['recent_assessments'] = UserAssessment.objects.filter(
            is_completed=True,
            completed_at__gte=thirty_days_ago
        ).count()
        
        # Mood entries
        context['total_mood_entries'] = MoodEntry.objects.count()
        context['recent_mood_entries'] = MoodEntry.objects.filter(date__gte=thirty_days_ago).count()
        
        # Average mood score
        from django.db.models import Avg
        avg_mood = MoodEntry.objects.aggregate(avg_mood=Avg('mood'))['avg_mood']
        context['average_mood'] = round(avg_mood, 2) if avg_mood else 0
        
        # Critical cases that need attention
        severe_results = AssessmentResult.objects.filter(
            severity_level__in=['moderately_severe', 'severe']
        ).order_by('-created_at')[:10]
        context['severe_cases'] = severe_results
        
        # Monthly user registration trends
        monthly_users = {}
        for i in range(12):
            month_start = timezone.now() - timedelta(days=30*i)
            month_end = timezone.now() - timedelta(days=30*(i-1)) if i > 0 else timezone.now()
            count = User.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            monthly_users[month_start.strftime('%Y-%m')] = count
        
        context['monthly_users'] = monthly_users
        
        return context

class AdminUserManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = User
    template_name = 'core/admin_user_management.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('-created_at')
        
        # Filter by role
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role_filter'] = self.request.GET.get('role', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class AdminUserDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = User
    template_name = 'core/admin_user_detail.html'
    context_object_name = 'user_detail'
    pk_url_kwarg = 'user_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        # Get user's mood entries
        context['mood_entries'] = MoodEntry.objects.filter(user=user).order_by('-date')[:10]
        
        # Get user's assessments
        from screening.models import UserAssessment, AssessmentResult
        
        user_assessments = UserAssessment.objects.filter(user=user, is_completed=True).order_by('-completed_at')
        context['assessments'] = user_assessments[:10]
        
        # Get latest assessment results
        latest_results = AssessmentResult.objects.filter(
            user_assessment__user=user,
            user_assessment__is_completed=True
        ).order_by('-created_at')[:5]
        context['latest_results'] = latest_results
        
        # Check if user needs attention
        context['needs_attention'] = any(
            result.severity_level in ['moderately_severe', 'severe'] 
            for result in latest_results
        )
        
        # Organization details if user is organization
        if user.role == 'organization':
            try:
                context['organization'] = user.organization_profile
            except Organization.DoesNotExist:
                context['organization'] = None
        
        return context

class AdminOrganizationManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Organization
    template_name = 'core/admin_organization_management.html'
    context_object_name = 'organizations'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Organization.objects.all().order_by('-created_at')
        
        # Filter by verification status
        verified = self.request.GET.get('verified')
        if verified == 'true':
            queryset = queryset.filter(is_verified=True)
        elif verified == 'false':
            queryset = queryset.filter(is_verified=False)
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(organization_name__icontains=search) |
                Q(city__icontains=search) |
                Q(organization_type__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verified_filter'] = self.request.GET.get('verified', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class AdminOrganizationDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = Organization
    template_name = 'core/admin_organization_detail.html'
    context_object_name = 'organization'
    pk_url_kwarg = 'org_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = self.get_object()
        
        # Get organization staff
        context['staff'] = OrganizationStaff.objects.filter(
            organization=organization
        ).order_by('-joined_at')
        
        return context

@login_required
@user_passes_test(is_admin)
def admin_analytics_view(request):
    """Admin analytics view with detailed statistics"""
    from screening.models import UserAssessment, AssessmentResult
    from collections import OrderedDict
    
    context = {}
    
    # User analytics
    context['total_users'] = User.objects.count()
    context['active_users'] = User.objects.filter(is_active=True).count()
    context['regular_users'] = User.objects.filter(role='user').count()
    context['organizations'] = User.objects.filter(role='organization').count()
    
    # Total organizations (Organization model)
    context['total_organizations'] = Organization.objects.count()
    
    # Assessment analytics
    context['total_assessments'] = UserAssessment.objects.filter(is_completed=True).count()
    
    # Assessment type breakdown (for template: assessment_types)
    assessment_types = UserAssessment.objects.filter(is_completed=True).values(
        'assessment__name'
    ).annotate(count=Count('id')).order_by('-count')
    context['assessment_types'] = {item['assessment__name']: item['count'] for item in assessment_types}
    
    # Severity level distribution
    severity_distribution = AssessmentResult.objects.values('severity_level').annotate(
        count=Count('id')
    ).order_by('severity_level')
    context['severity_distribution'] = {item['severity_level']: item['count'] for item in severity_distribution}
    
    # Organization types breakdown
    org_types = Organization.objects.values('organization_type').annotate(
        count=Count('id')
    ).order_by('-count')
    context['org_types'] = {item['organization_type']: item['count'] for item in org_types}
    
    # Monthly user growth (last 12 months)
    monthly_users = OrderedDict()
    for i in range(11, -1, -1):  # Start from 11 months ago to now
        month_start = timezone.now() - timedelta(days=30*(i+1))
        month_end = timezone.now() - timedelta(days=30*i)
        
        # Use created_at field from custom User model
        users_count = User.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        month_key = month_start.strftime('%b')  # Short month name
        monthly_users[month_key] = users_count
    
    context['monthly_users'] = monthly_users
    
    # Mood analytics
    context['total_mood_entries'] = MoodEntry.objects.count()
    avg_mood = MoodEntry.objects.aggregate(avg_mood=Avg('mood'))['avg_mood']
    context['average_mood'] = round(avg_mood, 2) if avg_mood else 0
    
    return render(request, 'core/admin_analytics.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_toggle_user_status(request, user_id):
    """Toggle user active status"""
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    status = "activated" if user.is_active else "deactivated"
    
    if user.is_active:
        messages.success(request, f'User "{user.username}" has been {status}. They can now log in.')
    else:
        messages.warning(
            request, 
            f'User "{user.username}" has been {status}. '
            f'They will be automatically logged out and redirected to the account suspended page on their next request. '
            f'They will not be able to log in until reactivated.'
        )
    
    return redirect('core:admin_user_detail', user_id=user_id)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_toggle_organization_verification(request, org_id):
    """Toggle organization verification status"""
    organization = get_object_or_404(Organization, id=org_id)
    organization.is_verified = not organization.is_verified
    organization.save()
    
    status = "verified" if organization.is_verified else "unverified"
    messages.success(request, f'Organization {organization.organization_name} has been {status}.')
    
    return redirect('core:admin_organization_detail', org_id=org_id)

class AdminCreateOrganizationView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Admin view to manually create organization accounts"""
    template_name = 'core/admin_create_organization.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AdminOrganizationCreationForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = AdminOrganizationCreationForm(request.POST)
        
        if form.is_valid():
            try:
                user, organization = form.save()
                
                # Send welcome email if requested
                if form.cleaned_data.get('send_welcome_email'):
                    self.send_welcome_email(user, form.cleaned_data['password'])
                
                messages.success(
                    request, 
                    f'Organization "{organization.organization_name}" has been created successfully! '
                    f'Username: {user.username}'
                )
                return redirect('core:admin_organization_detail', org_id=organization.id)
                
            except Exception as e:
                messages.error(request, f'Error creating organization: {str(e)}')
        
        return self.render_to_response({'form': form})
    
    def send_welcome_email(self, user, password):
        """Send welcome email to the new organization (placeholder for email functionality)"""
        # This is a placeholder - you can implement actual email sending here
        # For now, we'll just add a success message
        messages.info(
            self.request,
            f'Welcome email would be sent to {user.email} with login credentials. '
            f'(Email functionality needs to be configured)'
        )

@login_required
@user_passes_test(is_admin)
def admin_organization_quick_actions(request):
    """AJAX endpoint for quick organization actions"""
    if request.method == 'POST':
        action = request.POST.get('action')
        org_id = request.POST.get('org_id')
        
        try:
            organization = get_object_or_404(Organization, id=org_id)
            
            if action == 'verify':
                organization.is_verified = True
                organization.save()
                return JsonResponse({
                    'success': True,
                    'message': f'{organization.organization_name} has been verified.'
                })
            
            elif action == 'unverify':
                organization.is_verified = False
                organization.save()
                return JsonResponse({
                    'success': True,
                    'message': f'{organization.organization_name} has been unverified.'
                })
            
            elif action == 'activate_user':
                organization.user.is_active = True
                organization.user.save()
                return JsonResponse({
                    'success': True,
                    'message': f'User account for {organization.organization_name} has been activated. They can now log in.'
                })
            
            elif action == 'deactivate_user':
                organization.user.is_active = False
                organization.user.save()
                return JsonResponse({
                    'success': True,
                    'message': f'User account for {organization.organization_name} has been deactivated. They will be logged out automatically and cannot log in until reactivated.'
                })
            
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid action.'
                })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

# User Edit, Create, and Delete Views

class AdminUserEditView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Admin view to edit user accounts"""
    template_name = 'core/admin_user_edit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        context['form'] = AdminUserEditForm(instance=user)
        context['edit_user'] = user
        return context
    
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        form = AdminUserEditForm(request.POST, instance=user)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'User "{user.username}" has been updated successfully!')
            return redirect('core:admin_user_detail', user_id=user_id)
        
        return self.render_to_response({'form': form, 'edit_user': user})

class AdminUserCreateView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Admin view to create new user accounts"""
    template_name = 'core/admin_user_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AdminUserCreateForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = AdminUserCreateForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            messages.success(
                request, 
                f'User "{user.username}" has been created successfully!'
            )
            return redirect('core:admin_user_detail', user_id=user.id)
        
        return self.render_to_response({'form': form})

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_delete_user(request, user_id):
    """Delete a user account"""
    user = get_object_or_404(User, id=user_id)
    
    # Prevent deleting self
    if user.id == request.user.id:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('core:admin_user_detail', user_id=user_id)
    
    # Prevent deleting superusers (unless you are one)
    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, 'You cannot delete a superuser account.')
        return redirect('core:admin_user_detail', user_id=user_id)
    
    username = user.username
    user.delete()
    messages.success(request, f'User "{username}" has been deleted successfully.')
    return redirect('core:admin_user_management')

class AdminOrganizationEditView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Admin view to edit organization profiles"""
    template_name = 'core/admin_organization_edit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org_id = kwargs.get('org_id')
        organization = get_object_or_404(Organization, id=org_id)
        context['form'] = AdminOrganizationEditForm(instance=organization)
        context['organization'] = organization
        return context
    
    def post(self, request, *args, **kwargs):
        org_id = kwargs.get('org_id')
        organization = get_object_or_404(Organization, id=org_id)
        form = AdminOrganizationEditForm(request.POST, instance=organization)
        
        if form.is_valid():
            form.save()
            messages.success(
                request, 
                f'Organization "{organization.organization_name}" has been updated successfully!'
            )
            return redirect('core:admin_organization_detail', org_id=org_id)
        
        return self.render_to_response({'form': form, 'organization': organization})

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_delete_organization(request, org_id):
    """Delete an organization and its associated user account"""
    organization = get_object_or_404(Organization, id=org_id)
    user = organization.user
    
    # Prevent deleting if the organization user is the current admin
    if user.id == request.user.id:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('core:admin_organization_detail', org_id=org_id)
    
    org_name = organization.organization_name
    user.delete()  # This will cascade delete the organization
    messages.success(request, f'Organization "{org_name}" and its associated account have been deleted successfully.')
    return redirect('core:admin_organization_management')

# Assessment Management Views

class AdminAssessmentManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Admin view to manage all assessments"""
    model = Assessment
    template_name = 'core/admin_assessment_management.html'
    context_object_name = 'assessments'
    
    def get_queryset(self):
        return Assessment.objects.all().order_by('name', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add assessment statistics
        context['total_assessments'] = Assessment.objects.count()
        context['active_assessments'] = Assessment.objects.filter(is_active=True).count()
        context['total_user_assessments'] = UserAssessment.objects.filter(is_completed=True).count()
        return context

class AdminAssessmentDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """Admin view to see assessment details"""
    model = Assessment
    template_name = 'core/admin_assessment_detail.html'
    pk_url_kwarg = 'assessment_id'
    context_object_name = 'assessment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assessment = self.get_object()
        context['questions'] = assessment.questions.all()
        context['user_assessments'] = UserAssessment.objects.filter(
            assessment=assessment, 
            is_completed=True
        ).count()
        return context

class AdminAssessmentCreateView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Admin view to create new assessments"""
    template_name = 'core/admin_assessment_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AssessmentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = AssessmentForm(request.POST)
        
        if form.is_valid():
            assessment = form.save()
            messages.success(
                request,
                f'Assessment "{assessment.title}" has been created successfully!'
            )
            return redirect('core:admin_assessment_detail', assessment_id=assessment.id)
        
        return self.render_to_response({'form': form})

class AdminAssessmentEditView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Admin view to edit assessments"""
    template_name = 'core/admin_assessment_edit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assessment_id = kwargs.get('assessment_id')
        assessment = get_object_or_404(Assessment, id=assessment_id)
        context['assessment'] = assessment
        context['form'] = AssessmentForm(instance=assessment)
        return context
    
    def post(self, request, *args, **kwargs):
        assessment_id = kwargs.get('assessment_id')
        assessment = get_object_or_404(Assessment, id=assessment_id)
        form = AssessmentForm(request.POST, instance=assessment)
        
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Assessment "{assessment.title}" has been updated successfully!'
            )
            return redirect('core:admin_assessment_detail', assessment_id=assessment_id)
        
        return self.render_to_response({'form': form, 'assessment': assessment})

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_delete_assessment(request, assessment_id):
    """Delete an assessment"""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    
    # Check if assessment has been taken by users
    user_assessment_count = UserAssessment.objects.filter(assessment=assessment).count()
    
    if user_assessment_count > 0:
        messages.warning(
            request,
            f'Cannot delete "{assessment.title}" - it has been taken by {user_assessment_count} user(s). '
            f'You can deactivate it instead.'
        )
        return redirect('core:admin_assessment_detail', assessment_id=assessment_id)
    
    title = assessment.title
    assessment.delete()
    messages.success(request, f'Assessment "{title}" has been deleted successfully.')
    return redirect('core:admin_assessment_management')

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_toggle_assessment_status(request, assessment_id):
    """Toggle assessment active status"""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    assessment.is_active = not assessment.is_active
    assessment.save()
    
    status = "activated" if assessment.is_active else "deactivated"
    messages.success(request, f'Assessment "{assessment.title}" has been {status}.')
    
    return redirect('core:admin_assessment_detail', assessment_id=assessment_id)
