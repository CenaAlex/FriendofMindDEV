"""
Views for Forum/Community System
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q, Count, Prefetch
from .forum_models import ForumPost, ForumComment, ForumLike, ForumReport, ForumCommentReport
from .forum_forms import ForumPostForm, ForumCommentForm, ForumReportForm, ForumCommentReportForm
from .feedback_models import Notification
from .models import User


# Forum List & Post Views

class ForumListView(LoginRequiredMixin, ListView):
    """View all forum posts"""
    model = ForumPost
    template_name = 'core/forum_list.html'
    context_object_name = 'posts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ForumPost.objects.filter(is_hidden=False).select_related('author').prefetch_related(
            'likes',
            Prefetch('comments', queryset=ForumComment.objects.filter(is_hidden=False).select_related('author'))
        ).annotate(
            like_count=Count('likes', distinct=True),
            comment_count=Count('comments', filter=Q(comments__is_hidden=False), distinct=True)
        )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_form'] = ForumPostForm()
        context['total_posts'] = ForumPost.objects.filter(is_hidden=False).count()
        return context


class ForumPostDetailView(LoginRequiredMixin, DetailView):
    """View single post with comments"""
    model = ForumPost
    template_name = 'core/forum_post_detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'
    
    def get_queryset(self):
        return ForumPost.objects.filter(is_hidden=False).select_related('author').prefetch_related(
            'likes',
            Prefetch('comments', queryset=ForumComment.objects.filter(is_hidden=False).select_related('author').order_by('created_at'))
        )
    
    def get(self, request, *args, **kwargs):
        """Handle case where post doesn't exist or is hidden"""
        try:
            return super().get(request, *args, **kwargs)
        except:
            messages.warning(request, 'This post is no longer available. It may have been deleted or removed.')
            return redirect('core:forum_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = ForumCommentForm()
        context['report_form'] = ForumReportForm()
        context['is_liked'] = self.object.is_liked_by(self.request.user)
        return context


@login_required
def create_post(request):
    """Create a new forum post"""
    if request.method == 'POST':
        form = ForumPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Your post has been created successfully!')
            return redirect('core:forum_post_detail', post_id=post.id)
        else:
            messages.error(request, 'Please correct the errors below.')
            # Return to forum list with errors
            posts = ForumPost.objects.filter(is_hidden=False).select_related('author').order_by('-created_at')[:20]
            return render(request, 'core/forum_list.html', {
                'posts': posts,
                'post_form': form,
                'total_posts': ForumPost.objects.filter(is_hidden=False).count()
            })
    
    return redirect('core:forum_list')


@login_required
def edit_post(request, post_id):
    """Edit a forum post"""
    post = get_object_or_404(ForumPost, id=post_id)
    
    if not post.can_edit(request.user):
        messages.error(request, 'You do not have permission to edit this post.')
        return redirect('core:forum_post_detail', post_id=post_id)
    
    if request.method == 'POST':
        form = ForumPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)
            updated_post.is_edited = True
            updated_post.save()
            messages.success(request, 'Your post has been updated!')
            return redirect('core:forum_post_detail', post_id=post_id)
    else:
        form = ForumPostForm(instance=post)
    
    return render(request, 'core/forum_edit_post.html', {
        'form': form,
        'post': post
    })


@login_required
def delete_post(request, post_id):
    """Delete a forum post"""
    post = get_object_or_404(ForumPost, id=post_id)
    
    if not post.can_delete(request.user):
        messages.error(request, 'You do not have permission to delete this post.')
        return redirect('core:forum_post_detail', post_id=post_id)
    
    if request.method == 'POST':
        # Delete related notifications to prevent broken links
        Notification.objects.filter(link_url__contains=f'/forum/post/{post_id}/').delete()
        post.delete()
        messages.success(request, 'Post has been deleted.')
        return redirect('core:forum_list')
    
    return render(request, 'core/forum_confirm_delete.html', {'post': post})


# Like/Unlike Actions

@login_required
@require_http_methods(["POST"])
def toggle_like(request, post_id):
    """Like or unlike a post"""
    post = get_object_or_404(ForumPost, id=post_id, is_hidden=False)
    
    # Check if already liked
    existing_like = ForumLike.objects.filter(post=post, user=request.user).first()
    
    if existing_like:
        # Unlike
        existing_like.delete()
        liked = False
    else:
        # Like
        ForumLike.objects.create(post=post, user=request.user)
        liked = True
        
        # Notify post author (if not liking own post)
        if post.author != request.user:
            Notification.objects.create(
                user=post.author,
                notification_type='system',
                title='New Like on Your Post',
                message=f'{request.user.get_full_name() or request.user.username} liked your post',
                link_url=f'/forum/post/{post.id}/'
            )
    
    return JsonResponse({
        'success': True,
        'liked': liked,
        'like_count': post.like_count()
    })


# Comment Actions

@login_required
def add_comment(request, post_id):
    """Add a comment to a post"""
    post = get_object_or_404(ForumPost, id=post_id, is_hidden=False)
    
    if request.method == 'POST':
        form = ForumCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            
            # Notify post author (if not commenting on own post)
            if post.author != request.user:
                Notification.objects.create(
                    user=post.author,
                    notification_type='system',
                    title='New Comment on Your Post',
                    message=f'{request.user.get_full_name() or request.user.username} commented on your post',
                    link_url=f'/forum/post/{post.id}/'
                )
            
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Please enter a comment.')
    
    return redirect('core:forum_post_detail', post_id=post_id)


@login_required
def edit_comment(request, comment_id):
    """Edit a comment"""
    comment = get_object_or_404(ForumComment, id=comment_id)
    
    if not comment.can_edit(request.user):
        messages.error(request, 'You do not have permission to edit this comment.')
        return redirect('core:forum_post_detail', post_id=comment.post.id)
    
    if request.method == 'POST':
        form = ForumCommentForm(request.POST, instance=comment)
        if form.is_valid():
            updated_comment = form.save(commit=False)
            updated_comment.is_edited = True
            updated_comment.save()
            messages.success(request, 'Comment updated!')
            return redirect('core:forum_post_detail', post_id=comment.post.id)
    else:
        form = ForumCommentForm(instance=comment)
    
    return render(request, 'core/forum_edit_comment.html', {
        'form': form,
        'comment': comment
    })


@login_required
def delete_comment(request, comment_id):
    """Delete a comment"""
    comment = get_object_or_404(ForumComment, id=comment_id)
    
    if not comment.can_delete(request.user):
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('core:forum_post_detail', post_id=comment.post.id)
    
    post_id = comment.post.id
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted.')
    
    return redirect('core:forum_post_detail', post_id=post_id)


# Report Actions

@login_required
def report_post(request, post_id):
    """Report a post"""
    post = get_object_or_404(ForumPost, id=post_id)
    
    # Check if user already reported this post
    existing_report = ForumReport.objects.filter(post=post, reporter=request.user).first()
    if existing_report:
        messages.warning(request, 'You have already reported this post.')
        return redirect('core:forum_post_detail', post_id=post_id)
    
    if request.method == 'POST':
        form = ForumReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.post = post
            report.reporter = request.user
            report.save()
            
            # Mark post as flagged
            post.is_flagged = True
            post.save()
            
            # Notify all admins
            admin_users = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True))
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    notification_type='admin',
                    title='Post Reported',
                    message=f'A post by {post.author.username} has been reported for {report.get_reason_display()}',
                    link_url=f'/system-admin/forum/reports/'
                )
            
            messages.success(request, 'Thank you for your report. Our team will review it shortly.')
            return redirect('core:forum_post_detail', post_id=post_id)
    else:
        form = ForumReportForm()
    
    return render(request, 'core/forum_report_post.html', {
        'form': form,
        'post': post
    })


@login_required
def report_comment(request, comment_id):
    """Report a comment"""
    comment = get_object_or_404(ForumComment, id=comment_id)
    
    # Check if user already reported this comment
    existing_report = ForumCommentReport.objects.filter(comment=comment, reporter=request.user).first()
    if existing_report:
        messages.warning(request, 'You have already reported this comment.')
        return redirect('core:forum_post_detail', post_id=comment.post.id)
    
    if request.method == 'POST':
        form = ForumCommentReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.comment = comment
            report.reporter = request.user
            report.save()
            
            # Mark comment as flagged
            comment.is_flagged = True
            comment.save()
            
            # Notify all admins
            admin_users = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True))
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    notification_type='admin',
                    title='Comment Reported',
                    message=f'A comment by {comment.author.username} has been reported for {report.get_reason_display()}',
                    link_url=f'/system-admin/forum/comment-reports/'
                )
            
            messages.success(request, 'Thank you for your report. Our team will review it shortly.')
            return redirect('core:forum_post_detail', post_id=comment.post.id)
    else:
        form = ForumCommentReportForm()
    
    return render(request, 'core/forum_report_comment.html', {
        'form': form,
        'comment': comment
    })


# User's own posts

@login_required
def my_posts(request):
    """View user's own posts"""
    posts = ForumPost.objects.filter(author=request.user).select_related('author').prefetch_related(
        'likes', 'comments'
    ).annotate(
        like_count=Count('likes', distinct=True),
        comment_count=Count('comments', filter=Q(comments__is_hidden=False), distinct=True)
    ).order_by('-created_at')
    
    context = {
        'posts': posts,
        'total_posts': posts.count()
    }
    
    return render(request, 'core/forum_my_posts.html', context)

