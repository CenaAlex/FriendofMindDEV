"""
Admin Mood Analytics Views - Aggregate data from all users
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Avg, Count, Q
from datetime import datetime, timedelta
from collections import defaultdict
from .models import MoodEntry, User


def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_mood_analytics(request):
    """Comprehensive mood analytics for all users"""
    # Get filter parameters
    days = int(request.GET.get('days', 30))  # Default 30 days
    
    # Calculate date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Get all mood entries for the period (ALL USERS)
    all_mood_entries = MoodEntry.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).select_related('user')
    
    # Get total users who logged mood
    active_users_count = all_mood_entries.values('user').distinct().count()
    total_users = User.objects.filter(
        is_staff=False, 
        is_superuser=False,
        is_active=True
    ).count()
    
    # Calculate statistics
    total_entries = all_mood_entries.count()
    
    if total_entries > 0:
        # Average mood across all users
        avg_mood = all_mood_entries.aggregate(Avg('mood'))['mood__avg']
        
        # Categorize moods
        very_happy_count = all_mood_entries.filter(mood=5).count()
        happy_count = all_mood_entries.filter(mood=4).count()
        neutral_count = all_mood_entries.filter(mood=3).count()
        sad_count = all_mood_entries.filter(mood=2).count()
        very_sad_count = all_mood_entries.filter(mood=1).count()
        
        # Calculate percentages
        positive_days = very_happy_count + happy_count
        negative_days = sad_count + very_sad_count
        
        positive_percentage = (positive_days / total_entries) * 100 if total_entries > 0 else 0
        negative_percentage = (negative_days / total_entries) * 100 if total_entries > 0 else 0
        neutral_percentage = (neutral_count / total_entries) * 100 if total_entries > 0 else 0
        
        # User engagement metrics
        engagement_rate = (active_users_count / total_users) * 100 if total_users > 0 else 0
        avg_entries_per_user = total_entries / active_users_count if active_users_count > 0 else 0
        
        # Get entries with notes
        entries_with_notes_count = all_mood_entries.filter(
            notes__isnull=False
        ).exclude(notes='').count()
        notes_percentage = (entries_with_notes_count / total_entries) * 100 if total_entries > 0 else 0
        
        # Users needing attention (low average mood)
        users_needing_attention = []
        for user in User.objects.filter(is_staff=False, is_superuser=False, is_active=True):
            user_entries = all_mood_entries.filter(user=user)
            if user_entries.exists():
                user_avg_mood = user_entries.aggregate(Avg('mood'))['mood__avg']
                if user_avg_mood and user_avg_mood < 2.5:  # Below 2.5 average
                    users_needing_attention.append({
                        'user': user,
                        'avg_mood': round(user_avg_mood, 1),
                        'entry_count': user_entries.count(),
                        'last_entry': user_entries.order_by('-date').first()
                    })
        
        # Sort by lowest mood first
        users_needing_attention.sort(key=lambda x: x['avg_mood'])
        
        # Daily trend data (for chart)
        daily_data = []
        current_date = start_date
        while current_date <= end_date:
            day_entries = all_mood_entries.filter(date=current_date)
            if day_entries.exists():
                day_avg = day_entries.aggregate(Avg('mood'))['mood__avg']
            else:
                day_avg = None
            
            daily_data.append({
                'date': current_date,
                'avg_mood': round(day_avg, 1) if day_avg else None,
                'entry_count': day_entries.count()
            })
            current_date += timedelta(days=1)
        
        # Most active users
        most_active_users = []
        user_entry_counts = all_mood_entries.values('user').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        for item in user_entry_counts:
            user = User.objects.get(id=item['user'])
            user_mood_avg = all_mood_entries.filter(user=user).aggregate(Avg('mood'))['mood__avg']
            most_active_users.append({
                'user': user,
                'entry_count': item['count'],
                'avg_mood': round(user_mood_avg, 1) if user_mood_avg else 0
            })
        
    else:
        # No data
        avg_mood = 0
        very_happy_count = happy_count = neutral_count = sad_count = very_sad_count = 0
        positive_days = negative_days = 0
        positive_percentage = negative_percentage = neutral_percentage = 0
        engagement_rate = 0
        avg_entries_per_user = 0
        entries_with_notes_count = 0
        notes_percentage = 0
        users_needing_attention = []
        daily_data = []
        most_active_users = []
    
    context = {
        # Overall stats
        'total_entries': total_entries,
        'active_users_count': active_users_count,
        'total_users': total_users,
        'engagement_rate': round(engagement_rate, 1),
        'avg_entries_per_user': round(avg_entries_per_user, 1),
        'avg_mood': round(avg_mood, 1) if avg_mood else 0,
        
        # Mood distribution
        'very_happy_count': very_happy_count,
        'happy_count': happy_count,
        'neutral_count': neutral_count,
        'sad_count': sad_count,
        'very_sad_count': very_sad_count,
        'positive_days': positive_days,
        'negative_days': negative_days,
        'positive_percentage': round(positive_percentage, 1),
        'negative_percentage': round(negative_percentage, 1),
        'neutral_percentage': round(neutral_percentage, 1),
        
        # Notes metrics
        'entries_with_notes_count': entries_with_notes_count,
        'notes_percentage': round(notes_percentage, 1),
        
        # User insights
        'users_needing_attention': users_needing_attention[:10],  # Top 10
        'most_active_users': most_active_users,
        
        # Time series data
        'daily_data': daily_data,
        
        # Filter
        'days_filter': days,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'core/admin_mood_analytics.html', context)

