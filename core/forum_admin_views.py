"""
Admin Views for Forum Moderation
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from .forum_models import ForumPost, ForumComment, ForumReport, ForumCommentReport
from .forum_forms import AdminReportReviewForm, AdminCommentReportReviewForm
from .feedback_models import Notification
from .models import User


def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser or user.is_staff


class AdminForumModerationView(LoginRequiredMixin, TemplateView):
    """Main admin forum moderation dashboard"""
    template_name = 'core/admin_forum_moderation.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics
        context['total_posts'] = ForumPost.objects.count()
        context['flagged_posts'] = ForumPost.objects.filter(is_flagged=True).count()
        context['hidden_posts'] = ForumPost.objects.filter(is_hidden=True).count()
        context['pending_post_reports'] = ForumReport.objects.filter(status='pending').count()
        context['pending_comment_reports'] = ForumCommentReport.objects.filter(status='pending').count()
        context['total_comments'] = ForumComment.objects.count()
        context['flagged_comments'] = ForumComment.objects.filter(is_flagged=True).count()
        
        # Recent reports
        context['recent_post_reports'] = ForumReport.objects.select_related(
            'post', 'post__author', 'reporter'
        ).order_by('-created_at')[:10]
        
        context['recent_comment_reports'] = ForumCommentReport.objects.select_related(
            'comment', 'comment__author', 'reporter'
        ).order_by('-created_at')[:10]
        
        return context


class AdminPostReportsView(LoginRequiredMixin, TemplateView):
    """View all post reports"""
    template_name = 'core/admin_post_reports.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters
        status_filter = self.request.GET.get('status', '')
        reason_filter = self.request.GET.get('reason', '')
        
        # Base queryset
        reports = ForumReport.objects.select_related(
            'post', 'post__author', 'reporter', 'reviewed_by'
        ).prefetch_related('post__reports')
        
        # Apply filters
        if status_filter:
            reports = reports.filter(status=status_filter)
        if reason_filter:
            reports = reports.filter(reason=reason_filter)
        
        # Order by pending first, then by date
        reports = reports.order_by(
            '-status',  # Pending comes before others
            '-created_at'
        )
        
        context['reports'] = reports
        context['status_filter'] = status_filter
        context['reason_filter'] = reason_filter
        context['pending_count'] = ForumReport.objects.filter(status='pending').count()
        context['total_count'] = ForumReport.objects.count()
        
        return context


class AdminCommentReportsView(LoginRequiredMixin, TemplateView):
    """View all comment reports"""
    template_name = 'core/admin_comment_reports.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters
        status_filter = self.request.GET.get('status', '')
        reason_filter = self.request.GET.get('reason', '')
        
        # Base queryset
        reports = ForumCommentReport.objects.select_related(
            'comment', 'comment__author', 'comment__post', 'reporter', 'reviewed_by'
        ).prefetch_related('comment__comment_reports')
        
        # Apply filters
        if status_filter:
            reports = reports.filter(status=status_filter)
        if reason_filter:
            reports = reports.filter(reason=reason_filter)
        
        # Order by pending first, then by date
        reports = reports.order_by(
            '-status',
            '-created_at'
        )
        
        context['reports'] = reports
        context['status_filter'] = status_filter
        context['reason_filter'] = reason_filter
        context['pending_count'] = ForumCommentReport.objects.filter(status='pending').count()
        context['total_count'] = ForumCommentReport.objects.count()
        
        return context


@login_required
@user_passes_test(is_admin)
def admin_review_post_report(request, report_id):
    """Review and take action on a post report"""
    report = get_object_or_404(ForumReport, id=report_id)
    post = report.post
    
    if request.method == 'POST':
        action = request.POST.get('action')
        form = AdminReportReviewForm(request.POST, instance=report)
        
        if form.is_valid():
            updated_report = form.save(commit=False)
            updated_report.reviewed_by = request.user
            updated_report.reviewed_at = timezone.now()
            
            if action == 'hide_post':
                post.is_hidden = True
                post.save()
                updated_report.status = 'action_taken'
                messages.success(request, 'Post has been hidden.')
                
                # Notify post author
                Notification.objects.create(
                    user=post.author,
                    notification_type='admin',
                    title='Your Post Was Hidden',
                    message='Your post was hidden by moderators for violating community guidelines.',
                    link_url='/forum/'
                )
            
            elif action == 'unhide_post':
                post.is_hidden = False
                post.save()
                messages.success(request, 'Post has been unhidden.')
            
            elif action == 'dismiss':
                post.is_flagged = False
                post.save()
                updated_report.status = 'dismissed'
                messages.success(request, 'Report has been dismissed.')
            
            elif action == 'delete_post':
                # Store author reference before deletion
                post_author = post.author
                post_title = post.content[:50] if post.content else 'Your post'
                
                # Notify post author BEFORE deleting (since post will be gone)
                Notification.objects.create(
                    user=post_author,
                    notification_type='admin',
                    title='Your Post Was Removed',
                    message=f'Your post "{post_title}..." was removed by moderators for violating community guidelines. Please review our community guidelines to ensure your future posts comply.',
                    link_url='/forum/'
                )
                
                # Delete related notifications that reference this post
                Notification.objects.filter(link_url__contains=f'/forum/post/{post.id}').delete()
                
                # Delete the post (report will be cascade-deleted automatically)
                post.delete()
                
                messages.success(request, 'Post has been permanently deleted and user notified.')
                return redirect('core:admin_post_reports')
            
            updated_report.save()
            return redirect('core:admin_post_reports')
    else:
        form = AdminReportReviewForm(instance=report)
    
    context = {
        'report': report,
        'post': post,
        'form': form,
        'all_reports': post.reports.select_related('reporter').order_by('-created_at')
    }
    
    return render(request, 'core/admin_review_post_report.html', context)


@login_required
@user_passes_test(is_admin)
def admin_review_comment_report(request, report_id):
    """Review and take action on a comment report"""
    report = get_object_or_404(ForumCommentReport, id=report_id)
    comment = report.comment
    
    if request.method == 'POST':
        action = request.POST.get('action')
        form = AdminCommentReportReviewForm(request.POST, instance=report)
        
        if form.is_valid():
            updated_report = form.save(commit=False)
            updated_report.reviewed_by = request.user
            updated_report.reviewed_at = timezone.now()
            
            if action == 'hide_comment':
                comment.is_hidden = True
                comment.save()
                updated_report.status = 'action_taken'
                messages.success(request, 'Comment has been hidden.')
                
                # Notify comment author
                Notification.objects.create(
                    user=comment.author,
                    notification_type='admin',
                    title='Your Comment Was Hidden',
                    message='Your comment was hidden by moderators for violating community guidelines.',
                    link_url='/forum/'
                )
            
            elif action == 'unhide_comment':
                comment.is_hidden = False
                comment.save()
                messages.success(request, 'Comment has been unhidden.')
            
            elif action == 'dismiss':
                comment.is_flagged = False
                comment.save()
                updated_report.status = 'dismissed'
                messages.success(request, 'Report has been dismissed.')
            
            elif action == 'delete_comment':
                # Store author reference before deletion
                comment_author = comment.author
                comment_content = comment.content[:50] if comment.content else 'Your comment'
                
                # Notify comment author BEFORE deleting
                Notification.objects.create(
                    user=comment_author,
                    notification_type='admin',
                    title='Your Comment Was Removed',
                    message=f'Your comment "{comment_content}..." was removed by moderators for violating community guidelines. Please review our community guidelines to ensure your future comments comply.',
                    link_url='/forum/'
                )
                
                # Delete the comment (report will be cascade-deleted automatically)
                comment.delete()
                
                messages.success(request, 'Comment has been permanently deleted and user notified.')
                return redirect('core:admin_comment_reports')
            
            updated_report.save()
            return redirect('core:admin_comment_reports')
    else:
        form = AdminCommentReportReviewForm(instance=report)
    
    context = {
        'report': report,
        'comment': comment,
        'form': form,
        'all_reports': comment.comment_reports.select_related('reporter').order_by('-created_at')
    }
    
    return render(request, 'core/admin_review_comment_report.html', context)


@login_required
@user_passes_test(is_admin)
def admin_all_posts(request):
    """View all forum posts for admin"""
    posts = ForumPost.objects.select_related('author').prefetch_related(
        'likes', 'comments', 'reports'
    ).annotate(
        like_count=Count('likes', distinct=True),
        comment_count=Count('comments', distinct=True),
        report_count=Count('reports', distinct=True)
    ).order_by('-created_at')
    
    # Filters
    show_hidden = request.GET.get('show_hidden', 'false') == 'true'
    show_flagged_only = request.GET.get('flagged_only', 'false') == 'true'
    
    if not show_hidden:
        posts = posts.filter(is_hidden=False)
    
    if show_flagged_only:
        posts = posts.filter(is_flagged=True)
    
    context = {
        'posts': posts,
        'show_hidden': show_hidden,
        'show_flagged_only': show_flagged_only,
        'total_count': posts.count()
    }
    
    return render(request, 'core/admin_all_posts.html', context)

