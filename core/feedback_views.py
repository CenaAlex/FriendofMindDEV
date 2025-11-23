"""
Views for Feedback and Notification System
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q, Count
from .feedback_models import Feedback, FeedbackResponse, Notification
from .feedback_forms import FeedbackForm, FeedbackResponseForm, FeedbackUpdateForm
from .models import User


def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser or user.is_staff


# User Feedback Views

@login_required
@require_http_methods(["POST"])
def submit_feedback(request):
    """Handle feedback submission via AJAX"""
    form = FeedbackForm(request.POST)
    
    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.user = request.user
        feedback.save()
        
        # Create notifications for all admins
        admin_users = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True))
        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                notification_type='admin',
                title=f'New {feedback.get_feedback_type_display()}',
                message=f'{request.user.get_full_name() or request.user.username} submitted: {feedback.subject}',
                link_url=f'/system-admin/feedback/{feedback.id}/',
                related_feedback=feedback
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you! Your feedback has been submitted successfully.'
        })
    else:
        errors = {}
        for field, field_errors in form.errors.items():
            errors[field] = field_errors[0] if field_errors else ''
        
        return JsonResponse({
            'success': False,
            'message': 'Please correct the errors below.',
            'errors': errors
        })


@login_required
def my_feedback(request):
    """View user's own feedback submissions"""
    feedbacks = Feedback.objects.filter(user=request.user).prefetch_related('responses')
    
    context = {
        'feedbacks': feedbacks,
        'pending_count': feedbacks.filter(status='pending').count(),
        'resolved_count': feedbacks.filter(status='resolved').count(),
    }
    
    return render(request, 'core/my_feedback.html', context)


@login_required
def feedback_detail(request, feedback_id):
    """View specific feedback and its responses"""
    feedback = get_object_or_404(Feedback, id=feedback_id, user=request.user)
    responses = feedback.responses.filter(is_internal_note=False)
    
    context = {
        'feedback': feedback,
        'responses': responses,
    }
    
    return render(request, 'core/feedback_detail.html', context)


# Notification Views

@login_required
def notifications_list(request):
    """View all notifications"""
    notifications = Notification.objects.filter(user=request.user)
    
    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count(),
    }
    
    return render(request, 'core/notifications_list.html', context)


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    return JsonResponse({
        'success': True,
        'unread_count': Notification.objects.filter(user=request.user, is_read=False).count()
    })


@login_required
@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return JsonResponse({'success': True, 'unread_count': 0})


@login_required
def get_notifications(request):
    """Get recent notifications via AJAX"""
    notifications = Notification.objects.filter(user=request.user)[:10]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    notifications_data = []
    for notif in notifications:
        notifications_data.append({
            'id': notif.id,
            'type': notif.notification_type,
            'title': notif.title,
            'message': notif.message,
            'link_url': notif.link_url,
            'is_read': notif.is_read,
            'created_at': notif.created_at.strftime('%b %d, %Y %I:%M %p'),
            'time_ago': get_time_ago(notif.created_at)
        })
    
    return JsonResponse({
        'success': True,
        'notifications': notifications_data,
        'unread_count': unread_count
    })


def get_time_ago(datetime_obj):
    """Calculate time ago string"""
    now = timezone.now()
    diff = now - datetime_obj
    
    if diff.days > 7:
        return datetime_obj.strftime('%b %d, %Y')
    elif diff.days > 0:
        return f'{diff.days}d ago'
    elif diff.seconds >= 3600:
        return f'{diff.seconds // 3600}h ago'
    elif diff.seconds >= 60:
        return f'{diff.seconds // 60}m ago'
    else:
        return 'Just now'


# Admin Feedback Management Views

class AdminFeedbackManagementView(LoginRequiredMixin, TemplateView):
    """Admin view to manage all feedback"""
    template_name = 'core/admin_feedback_management.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters
        status_filter = self.request.GET.get('status', '')
        type_filter = self.request.GET.get('type', '')
        priority_filter = self.request.GET.get('priority', '')
        
        # Base queryset
        feedbacks = Feedback.objects.all().select_related('user').prefetch_related('responses')
        
        # Apply filters
        if status_filter:
            feedbacks = feedbacks.filter(status=status_filter)
        if type_filter:
            feedbacks = feedbacks.filter(feedback_type=type_filter)
        if priority_filter:
            feedbacks = feedbacks.filter(priority=priority_filter)
        
        # Statistics
        context['total_feedback'] = Feedback.objects.count()
        context['pending_feedback'] = Feedback.objects.filter(status='pending').count()
        context['resolved_feedback'] = Feedback.objects.filter(status='resolved').count()
        context['high_priority'] = Feedback.objects.filter(priority='high').count()
        
        context['feedbacks'] = feedbacks
        context['status_filter'] = status_filter
        context['type_filter'] = type_filter
        context['priority_filter'] = priority_filter
        
        return context


class AdminFeedbackDetailView(LoginRequiredMixin, TemplateView):
    """Admin view for feedback detail and responses"""
    template_name = 'core/admin_feedback_detail.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        feedback_id = kwargs.get('feedback_id')
        
        feedback = get_object_or_404(Feedback, id=feedback_id)
        context['feedback'] = feedback
        context['responses'] = feedback.responses.all()
        context['response_form'] = FeedbackResponseForm()
        context['update_form'] = FeedbackUpdateForm(instance=feedback)
        
        return context
    
    def post(self, request, *args, **kwargs):
        feedback_id = kwargs.get('feedback_id')
        feedback = get_object_or_404(Feedback, id=feedback_id)
        
        action = request.POST.get('action')
        
        if action == 'respond':
            form = FeedbackResponseForm(request.POST)
            if form.is_valid():
                response = form.save(commit=False)
                response.feedback = feedback
                response.admin_user = request.user
                response.save()
                
                # Update feedback status
                if feedback.status == 'pending':
                    feedback.status = 'in_review'
                    feedback.save()
                
                # Create notification for user if not internal note
                if not response.is_internal_note:
                    Notification.objects.create(
                        user=feedback.user,
                        notification_type='feedback_response',
                        title=f'Response to your {feedback.get_feedback_type_display()}',
                        message=f'An admin has responded to your feedback: "{feedback.subject}"',
                        link_url=f'/my-feedback/{feedback.id}/',
                        related_feedback=feedback
                    )
                
                messages.success(request, 'Response added successfully!')
                return redirect('core:admin_feedback_detail', feedback_id=feedback_id)
        
        elif action == 'update_status':
            form = FeedbackUpdateForm(request.POST, instance=feedback)
            if form.is_valid():
                updated_feedback = form.save(commit=False)
                
                # Track if status changed to resolved
                if updated_feedback.status == 'resolved' and feedback.status != 'resolved':
                    updated_feedback.resolved_at = timezone.now()
                    updated_feedback.resolved_by = request.user
                    
                    # Notify user
                    Notification.objects.create(
                        user=feedback.user,
                        notification_type='feedback_status',
                        title=f'Your {feedback.get_feedback_type_display()} was resolved',
                        message=f'Your feedback "{feedback.subject}" has been marked as resolved.',
                        link_url=f'/my-feedback/{feedback.id}/',
                        related_feedback=feedback
                    )
                
                updated_feedback.save()
                messages.success(request, 'Feedback updated successfully!')
                return redirect('core:admin_feedback_detail', feedback_id=feedback_id)
        
        return self.get(request, *args, **kwargs)

