"""
Enhanced Resource Views with Bookmarking, Reporting, and Admin Management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy
from django.db.models import Q
from .models import (
    MentalHealthResource, ResourceCategory, UserResourceInteraction
)
from .forms import MentalHealthResourceForm
from core.feedback_models import Feedback


def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser or user.is_staff


# User Views - Bookmarking

@login_required
def bookmark_resource(request, resource_id):
    """Bookmark or unbookmark a resource"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
    
    try:
        # Get resource (allow bookmarking even inactive resources for admins)
        if request.user.is_staff or request.user.is_superuser:
            resource = get_object_or_404(MentalHealthResource, id=resource_id)
        else:
            resource = get_object_or_404(MentalHealthResource, id=resource_id, is_active=True)
        
        # Check if already bookmarked
        existing = UserResourceInteraction.objects.filter(
            user=request.user,
            resource=resource,
            interaction_type='bookmarked'
        ).first()
        
        if existing:
            # Remove bookmark
            existing.delete()
            bookmarked = False
            message = 'Resource removed from bookmarks'
        else:
            # Add bookmark
            UserResourceInteraction.objects.create(
                user=request.user,
                resource=resource,
                interaction_type='bookmarked'
            )
            bookmarked = True
            message = 'Resource bookmarked successfully'
        
        return JsonResponse({
            'success': True,
            'bookmarked': bookmarked,
            'message': message
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@login_required
def my_bookmarks(request):
    """View user's bookmarked resources"""
    bookmarks = UserResourceInteraction.objects.filter(
        user=request.user,
        interaction_type='bookmarked'
    ).select_related('resource', 'resource__category').order_by('-created_at')
    
    context = {
        'bookmarks': bookmarks,
        'total_bookmarks': bookmarks.count()
    }
    
    return render(request, 'mentalhealth/my_bookmarks.html', context)


# User Views - Reporting

@login_required
def report_resource(request, resource_id):
    """Report inaccurate or inappropriate resource"""
    resource = get_object_or_404(MentalHealthResource, id=resource_id)
    
    if request.method == 'POST':
        issue_description = request.POST.get('description', '').strip()
        
        if not issue_description:
            messages.error(request, 'Please provide details about the issue.')
            return redirect('mentalhealth:resource_detail', resource_id=resource_id)
        
        # Create feedback entry for admin review
        feedback = Feedback.objects.create(
            user=request.user,
            feedback_type='issue',
            subject=f'Resource Issue Report: {resource.title}',
            message=f'Resource ID: {resource.id}\n'
                   f'Resource Title: {resource.title}\n'
                   f'Resource Type: {resource.get_resource_type_display()}\n'
                   f'Category: {resource.category.name}\n\n'
                   f'Issue Description:\n{issue_description}'
        )
        
        # Create notification for all admins
        from core.models import User
        from core.feedback_models import Notification
        from django.urls import reverse
        
        admins = User.objects.filter(is_staff=True) | User.objects.filter(is_superuser=True)
        for admin in admins.distinct():
            Notification.objects.create(
                user=admin,
                notification_type='admin',
                title=f'New Resource Issue Report',
                message=f'{request.user.get_full_name() or request.user.username} reported an issue with: {resource.title}',
                link_url=reverse('core:admin_feedback_detail', kwargs={'feedback_id': feedback.id}),
                related_feedback=feedback
            )
        
        # Show success message with link to view report
        messages.success(
            request, 
            'Thank you! Your report has been submitted and will be reviewed by our team.'
        )
        
        # Redirect to feedback detail page so user can view their report
        return redirect('core:feedback_detail', feedback_id=feedback.id)
    
    context = {
        'resource': resource
    }
    
    return render(request, 'mentalhealth/report_resource.html', context)


# Enhanced Resource Detail with Bookmark Status

class ResourceDetailView(LoginRequiredMixin, DetailView):
    """View individual resource with bookmark status"""
    model = MentalHealthResource
    template_name = 'mentalhealth/resource_detail.html'
    pk_url_kwarg = 'resource_id'
    context_object_name = 'resource'
    
    def get_queryset(self):
        # Admins can see all, users only see active
        if self.request.user.is_staff or self.request.user.is_superuser:
            return MentalHealthResource.objects.all()
        return MentalHealthResource.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if bookmarked
        context['is_bookmarked'] = UserResourceInteraction.objects.filter(
            user=self.request.user,
            resource=self.object,
            interaction_type='bookmarked'
        ).exists()
        
        # Record view
        UserResourceInteraction.objects.create(
            user=self.request.user,
            resource=self.object,
            interaction_type='viewed'
        )
        
        return context


# Admin Views - Resource Management

class AdminResourceListView(LoginRequiredMixin, ListView):
    """Admin view of all resources"""
    model = MentalHealthResource
    template_name = 'mentalhealth/admin_resource_list.html'
    context_object_name = 'resources'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = MentalHealthResource.objects.all().select_related('category')
        
        # Filter by search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Filter by category
        category = self.request.GET.get('category', '')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by type
        resource_type = self.request.GET.get('type', '')
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ResourceCategory.objects.all()
        context['total_resources'] = MentalHealthResource.objects.count()
        context['active_resources'] = MentalHealthResource.objects.filter(is_active=True).count()
        context['search'] = self.request.GET.get('search', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_type'] = self.request.GET.get('type', '')
        context['current_status'] = self.request.GET.get('status', '')
        return context


class AdminResourceCreateView(LoginRequiredMixin, CreateView):
    """Admin create new resource"""
    model = MentalHealthResource
    form_class = MentalHealthResourceForm
    template_name = 'mentalhealth/admin_resource_form.html'
    success_url = reverse_lazy('mentalhealth:admin_resource_list')
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Resource created successfully!')
        return super().form_valid(form)


class AdminResourceUpdateView(LoginRequiredMixin, UpdateView):
    """Admin edit resource"""
    model = MentalHealthResource
    form_class = MentalHealthResourceForm
    template_name = 'mentalhealth/admin_resource_form.html'
    pk_url_kwarg = 'resource_id'
    success_url = reverse_lazy('mentalhealth:admin_resource_list')
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Resource updated successfully!')
        return super().form_valid(form)


@login_required
@user_passes_test(is_admin)
def admin_delete_resource(request, resource_id):
    """Admin delete resource"""
    resource = get_object_or_404(MentalHealthResource, id=resource_id)
    
    if request.method == 'POST':
        resource.delete()
        messages.success(request, f'Resource "{resource.title}" has been deleted.')
        return redirect('mentalhealth:admin_resource_list')
    
    context = {
        'resource': resource
    }
    
    return render(request, 'mentalhealth/admin_resource_delete.html', context)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_toggle_resource_status(request, resource_id):
    """Admin toggle resource active status"""
    resource = get_object_or_404(MentalHealthResource, id=resource_id)
    resource.is_active = not resource.is_active
    resource.save()
    
    status = 'activated' if resource.is_active else 'deactivated'
    messages.success(request, f'Resource "{resource.title}" has been {status}.')
    
    return redirect('mentalhealth:admin_resource_list')

