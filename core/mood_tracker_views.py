"""
Mood Tracker Popup Views
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
import random
from .models import MoodEntry


# Encouragement messages for low mood
ENCOURAGEMENT_MESSAGES = [
    "Remember, it's okay to not be okay. You're taking the right step by acknowledging your feelings.",
    "Every day is a new beginning. Take a deep breath and know that you're stronger than you think.",
    "Your mental health matters. We're here to support you on your journey to wellness.",
    "You're not alone in this. Many people face similar challenges, and help is available.",
    "Small steps lead to big changes. Be kind to yourself today.",
    "It's brave to acknowledge when you're struggling. That's the first step toward feeling better.",
    "Your feelings are valid. Take time to care for yourself today.",
    "Tough times don't last, but tough people do. You've got this.",
    "Remember to be gentle with yourself. Healing takes time.",
    "You're doing better than you think. Keep taking it one day at a time.",
]

# Supportive messages for medium mood
SUPPORTIVE_MESSAGES = [
    "Every day has its ups and downs. You're doing great by checking in with yourself.",
    "It's okay to feel neutral. Not every day has to be perfect.",
    "Thanks for being honest about how you're feeling. That takes courage.",
    "Remember, balance is key. Take care of yourself today.",
    "You're on the right track. Keep being mindful of your mental health.",
]

# Positive messages for good mood
POSITIVE_MESSAGES = [
    "That's wonderful! Keep up the positive energy!",
    "So glad to hear you're feeling good! Keep doing what's working for you.",
    "Great to see you're in a good mood! Your mental wellness journey is paying off.",
    "Fantastic! Remember this feeling for days when you need a reminder.",
    "That's amazing! Your positive mood can inspire others too.",
    "Wonderful news! Keep nurturing your mental health.",
]


@login_required
@require_http_methods(["GET"])
def check_mood_logged_today(request):
    """Check if user has logged mood today"""
    # Admins/staff don't log mood - they only view data
    if request.user.is_staff or request.user.is_superuser:
        return JsonResponse({
            'mood_logged': True  # Always return True for admins to prevent popup
        })
    
    today = timezone.now().date()
    
    # Check if user already logged mood today
    mood_logged = MoodEntry.objects.filter(
        user=request.user,
        date=today
    ).exists()
    
    return JsonResponse({
        'mood_logged': mood_logged
    })


@login_required
@require_http_methods(["POST"])
def log_mood(request):
    """Log user's mood and return personalized response"""
    # Prevent admins/staff from logging mood
    if request.user.is_staff or request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'message': 'Admins cannot log mood entries. You can view and analyze user data instead.'
        })
    
    try:
        mood_level = int(request.POST.get('mood_level'))
        notes = request.POST.get('notes', '').strip()
        
        if mood_level < 1 or mood_level > 5:
            return JsonResponse({
                'success': False,
                'message': 'Invalid mood level'
            })
        
        today = timezone.now().date()
        
        # Check if already logged today
        existing_entry = MoodEntry.objects.filter(
            user=request.user,
            date=today
        ).first()
        
        if existing_entry:
            # Update existing entry
            existing_entry.mood_level = mood_level
            existing_entry.notes = notes
            existing_entry.save()
        else:
            # Create new entry
            MoodEntry.objects.create(
                user=request.user,
                mood_level=mood_level,
                notes=notes,
                date=today
            )
        
        # Generate personalized response based on mood level
        if mood_level >= 4:  # Good mood (4-5)
            message = random.choice(POSITIVE_MESSAGES)
            suggestion = {
                'type': 'positive',
                'text': 'Keep up the great work! Consider:',
                'actions': [
                    {'text': 'Share your positivity in the forum', 'link': '/forum/'},
                    {'text': 'Explore wellness resources', 'link': '/mentalhealth/resources/'}
                ]
            }
        elif mood_level == 3:  # Neutral mood
            message = random.choice(SUPPORTIVE_MESSAGES)
            suggestion = {
                'type': 'neutral',
                'text': 'Here are some suggestions to enhance your day:',
                'actions': [
                    {'text': 'Check your mood trends', 'link': '/mood-history/'},
                    {'text': 'Browse helpful resources', 'link': '/mentalhealth/resources/'}
                ]
            }
        else:  # Low mood (1-2)
            message = random.choice(ENCOURAGEMENT_MESSAGES)
            suggestion = {
                'type': 'support',
                'text': 'We\'re here to support you. Consider:',
                'actions': [
                    {'text': 'Take a mental health assessment', 'link': '/screening/assessments/'},
                    {'text': 'Explore support resources', 'link': '/mentalhealth/resources/'},
                    {'text': 'Connect with the community', 'link': '/forum/'}
                ]
            }
        
        return JsonResponse({
            'success': True,
            'message': message,
            'suggestion': suggestion,
            'mood_level': mood_level
        })
        
    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'message': 'Invalid mood data'
        })


@login_required
def get_mood_stats(request):
    """Get user's mood statistics for display"""
    # Get last 30 days of mood entries
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    
    mood_entries = MoodEntry.objects.filter(
        user=request.user,
        date__gte=thirty_days_ago
    ).order_by('-date')
    
    if mood_entries.exists():
        avg_mood = sum(entry.mood_level for entry in mood_entries) / mood_entries.count()
        streak = calculate_streak(request.user)
    else:
        avg_mood = 0
        streak = 0
    
    return JsonResponse({
        'total_entries': mood_entries.count(),
        'average_mood': round(avg_mood, 1),
        'current_streak': streak
    })


def calculate_streak(user):
    """Calculate user's current streak of consecutive days logging mood"""
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

