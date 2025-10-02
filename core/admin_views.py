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
    context = {}
    
    # User analytics
    context['total_users'] = User.objects.count()
    context['active_users'] = User.objects.filter(is_active=True).count()
    context['regular_users'] = User.objects.filter(role='user').count()
    context['organizations'] = User.objects.filter(role='organization').count()
    
    # Assessment analytics
    from screening.models import UserAssessment, AssessmentResult
    
    context['total_assessments'] = UserAssessment.objects.filter(is_completed=True).count()
    
    # Assessment type breakdown
    assessment_types = UserAssessment.objects.filter(is_completed=True).values(
        'assessment__name'
    ).annotate(count=Count('id'))
    context['assessment_breakdown'] = {item['assessment__name']: item['count'] for item in assessment_types}
    
    # Severity level distribution
    severity_distribution = AssessmentResult.objects.values('severity_level').annotate(count=Count('id'))
    context['severity_distribution'] = {item['severity_level']: item['count'] for item in severity_distribution}
    
    # Monthly trends
    monthly_data = {}
    for i in range(12):
        month_start = timezone.now() - timedelta(days=30*i)
        month_end = timezone.now() - timedelta(days=30*(i-1)) if i > 0 else timezone.now()
        
        users_count = User.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        assessments_count = UserAssessment.objects.filter(
            is_completed=True,
            completed_at__gte=month_start,
            completed_at__lt=month_end
        ).count()
        
        month_key = month_start.strftime('%Y-%m')
        monthly_data[month_key] = {
            'users': users_count,
            'assessments': assessments_count
        }
    
    context['monthly_data'] = monthly_data
    
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
    messages.success(request, f'User {user.username} has been {status}.')
    
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
