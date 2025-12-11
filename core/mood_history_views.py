"""
Mood History and Summary Views
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.utils import timezone
from django.db.models import Avg, Count, Q
from datetime import datetime, timedelta
from collections import defaultdict
from .models import MoodEntry


@login_required
def mood_history_summary(request):
    """Comprehensive mood history summary with statistics and insights"""
    # Get filter parameters
    days = int(request.GET.get('days', 30))  # Default 30 days
    
    # Calculate date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Get mood entries for the period
    mood_entries = MoodEntry.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('-date')
    
    # Calculate statistics
    total_entries = mood_entries.count()
    
    if total_entries > 0:
        # Average mood
        avg_mood = mood_entries.aggregate(Avg('mood'))['mood__avg']
        
        # Categorize moods
        very_happy_count = mood_entries.filter(mood=5).count()
        happy_count = mood_entries.filter(mood=4).count()
        neutral_count = mood_entries.filter(mood=3).count()
        sad_count = mood_entries.filter(mood=2).count()
        very_sad_count = mood_entries.filter(mood=1).count()
        
        # Calculate percentages
        positive_days = very_happy_count + happy_count
        negative_days = sad_count + very_sad_count
        
        positive_percentage = (positive_days / total_entries) * 100 if total_entries > 0 else 0
        negative_percentage = (negative_days / total_entries) * 100 if total_entries > 0 else 0
        neutral_percentage = (neutral_count / total_entries) * 100 if total_entries > 0 else 0
        
        # Find most common mood
        mood_counts = {
            5: very_happy_count,
            4: happy_count,
            3: neutral_count,
            2: sad_count,
            1: very_sad_count
        }
        most_common_mood = max(mood_counts, key=mood_counts.get)
        mood_names = {1: 'Very Sad', 2: 'Sad', 3: 'Neutral', 4: 'Happy', 5: 'Very Happy'}
        
        # Calculate streak
        current_streak = calculate_mood_streak(request.user)
        
        # Get entries with notes
        entries_with_notes = mood_entries.filter(notes__isnull=False).exclude(notes='')
        
        # Analyze mood trends
        trend = analyze_mood_trend(mood_entries, days)
        
        # Generate insights
        insights = generate_mood_insights(
            avg_mood=avg_mood,
            positive_percentage=positive_percentage,
            negative_percentage=negative_percentage,
            most_common_mood=most_common_mood,
            trend=trend,
            total_entries=total_entries,
            days=days
        )
        
    else:
        # No data
        avg_mood = 0
        very_happy_count = happy_count = neutral_count = sad_count = very_sad_count = 0
        positive_days = negative_days = 0
        positive_percentage = negative_percentage = neutral_percentage = 0
        most_common_mood = 3
        mood_names = {1: 'Very Sad', 2: 'Sad', 3: 'Neutral', 4: 'Happy', 5: 'Very Happy'}
        current_streak = 0
        entries_with_notes = mood_entries.none()
        trend = 'stable'
        insights = []
    
    # Prepare chart data - mood entries ordered by date for line chart
    chart_entries = MoodEntry.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    chart_labels = []
    chart_data = []
    chart_colors = []
    
    for entry in chart_entries:
        chart_labels.append(entry.date.strftime('%b %d'))
        chart_data.append(entry.mood)
        # Color based on mood level
        if entry.mood >= 4:
            chart_colors.append('#22c55e')  # Green for happy
        elif entry.mood == 3:
            chart_colors.append('#3b82f6')  # Blue for neutral
        else:
            chart_colors.append('#ef4444')  # Red for sad
    
    import json
    
    context = {
        'mood_entries': mood_entries,
        'total_entries': total_entries,
        'avg_mood': round(avg_mood, 1) if avg_mood else 0,
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
        'most_common_mood': most_common_mood,
        'most_common_mood_name': mood_names[most_common_mood],
        'current_streak': current_streak,
        'entries_with_notes': entries_with_notes,
        'trend': trend,
        'insights': insights,
        'days_filter': days,
        'start_date': start_date,
        'end_date': end_date,
        # Chart data
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'chart_colors': json.dumps(chart_colors),
    }
    
    return render(request, 'core/mood_history_summary.html', context)


def calculate_mood_streak(user):
    """Calculate consecutive days of mood logging"""
    today = timezone.now().date()
    streak = 0
    current_date = today
    
    while True:
        if MoodEntry.objects.filter(user=user, date=current_date).exists():
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak


def analyze_mood_trend(mood_entries, days):
    """Analyze if mood is improving, declining, or stable"""
    if mood_entries.count() < 3:
        return 'stable'
    
    # Split entries into two halves
    half_point = mood_entries.count() // 2
    recent_entries = list(mood_entries[:half_point])
    older_entries = list(mood_entries[half_point:])
    
    if recent_entries and older_entries:
        recent_avg = sum(e.mood for e in recent_entries) / len(recent_entries)
        older_avg = sum(e.mood for e in older_entries) / len(older_entries)
        
        difference = recent_avg - older_avg
        
        if difference > 0.3:
            return 'improving'
        elif difference < -0.3:
            return 'declining'
        else:
            return 'stable'
    
    return 'stable'


def generate_mood_insights(avg_mood, positive_percentage, negative_percentage, 
                          most_common_mood, trend, total_entries, days):
    """Generate personalized insights based on mood data"""
    insights = []
    
    # Overall mood insight
    if avg_mood >= 4:
        insights.append({
            'type': 'positive',
            'icon': 'fa-smile-beam',
            'title': 'Great Mental Health!',
            'message': f'Your average mood over the past {days} days has been {avg_mood:.1f}/5. You\'re doing wonderfully!'
        })
    elif avg_mood >= 3:
        insights.append({
            'type': 'neutral',
            'icon': 'fa-meh',
            'title': 'Balanced Mood',
            'message': f'Your average mood is {avg_mood:.1f}/5. You\'re maintaining a stable emotional state.'
        })
    else:
        insights.append({
            'type': 'support',
            'icon': 'fa-heart',
            'title': 'You\'re Not Alone',
            'message': f'Your average mood has been {avg_mood:.1f}/5. Remember, it\'s okay to seek support when you need it.'
        })
    
    # Trend insight
    if trend == 'improving':
        insights.append({
            'type': 'positive',
            'icon': 'fa-chart-line',
            'title': 'Positive Trend!',
            'message': 'Your mood has been improving over time. Keep up whatever you\'re doing!'
        })
    elif trend == 'declining':
        insights.append({
            'type': 'warning',
            'icon': 'fa-exclamation-triangle',
            'title': 'Mood Declining',
            'message': 'Your mood has been declining recently. Consider taking an assessment or exploring support resources.'
        })
    
    # Positive days insight
    if positive_percentage > 60:
        insights.append({
            'type': 'positive',
            'icon': 'fa-sun',
            'title': 'Mostly Positive Days',
            'message': f'{positive_percentage:.0f}% of your days have been happy or very happy. That\'s excellent!'
        })
    elif negative_percentage > 50:
        insights.append({
            'type': 'support',
            'icon': 'fa-hand-holding-heart',
            'title': 'Challenging Times',
            'message': f'{negative_percentage:.0f}% of your days have been difficult. Please reach out for support if needed.'
        })
    
    # Consistency insight
    if total_entries >= days * 0.8:  # Logged 80%+ of days
        insights.append({
            'type': 'positive',
            'icon': 'fa-calendar-check',
            'title': 'Great Consistency!',
            'message': f'You\'ve logged your mood {total_entries} out of {days} days. Consistency is key to understanding your patterns!'
        })
    elif total_entries < days * 0.3:  # Logged less than 30%
        insights.append({
            'type': 'info',
            'icon': 'fa-calendar',
            'title': 'Log More Regularly',
            'message': 'Try to log your mood daily for better insights into your mental health patterns.'
        })
    
    return insights


@login_required
def mood_reasons_summary(request):
    """Summary of reasons/notes grouped by mood level"""
    days = int(request.GET.get('days', 30))
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Get entries with notes, grouped by mood
    happy_entries = MoodEntry.objects.filter(
        user=request.user,
        date__gte=start_date,
        mood__gte=4
    ).exclude(notes='').order_by('-date')
    
    neutral_entries = MoodEntry.objects.filter(
        user=request.user,
        date__gte=start_date,
        mood=3
    ).exclude(notes='').order_by('-date')
    
    sad_entries = MoodEntry.objects.filter(
        user=request.user,
        date__gte=start_date,
        mood__lte=2
    ).exclude(notes='').order_by('-date')
    
    context = {
        'happy_entries': happy_entries,
        'neutral_entries': neutral_entries,
        'sad_entries': sad_entries,
        'days_filter': days,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'core/mood_reasons_summary.html', context)

