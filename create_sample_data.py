#!/usr/bin/env python
"""
Script to create sample data for testing the FriendOfMind application.
Run this after creating a superuser.
"""
import os
import sys
import django
from django.utils import timezone
from datetime import timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'friendofmind.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import User, MoodEntry, Organization, OrganizationStaff
from screening.models import Assessment, Question, AnswerChoice, UserAssessment, UserAnswer, AssessmentResult
from mentalhealth.models import ResourceCategory, MentalHealthResource, ProfessionalContact, SelfHelpExercise

def create_sample_data():
    print("Creating sample data...")
    
    # Create sample users
    print("Creating sample users...")
    for i in range(10):
        username = f"user{i+1}"
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f"user{i+1}@example.com",
                password="password123",
                first_name=f"User{i+1}",
                last_name="Test",
                role='user'
            )
            print(f"Created user: {username}")
    
    # Create sample organization users
    print("Creating sample organizations...")
    for i in range(3):
        username = f"org{i+1}"
        if not User.objects.filter(username=username).exists():
            org_user = User.objects.create_user(
                username=username,
                email=f"org{i+1}@example.com",
                password="password123",
                first_name=f"Organization{i+1}",
                last_name="Admin",
                role='organization'
            )
            
            # Create organization profile
            Organization.objects.create(
                user=org_user,
                organization_name=f"Mental Health Center {i+1}",
                organization_type='mental_health_center',
                address=f"123 Health St {i+1}",
                city="Manila",
                state="Metro Manila",
                zip_code="1000",
                phone=f"02-123-456{i}",
                email=f"org{i+1}@example.com",
                description=f"A comprehensive mental health center providing various services.",
                is_verified=True if i == 0 else False
            )
            print(f"Created organization: {username}")
    
    # Create sample mood entries
    print("Creating sample mood entries...")
    users = User.objects.filter(role='user')[:5]
    for user in users:
        for days_ago in range(30):
            date = timezone.now() - timedelta(days=days_ago)
            mood = random.randint(1, 5)
            notes = [
                "Feeling good today!",
                "Had a rough day at work",
                "Spent time with family",
                "Feeling anxious about tomorrow",
                "Great weather lifted my spirits",
                ""
            ]
            MoodEntry.objects.get_or_create(
                user=user,
                date=date,
                defaults={
                    'mood': mood,
                    'notes': random.choice(notes)
                }
            )
    
    # Create assessments
    print("Creating assessments...")
    
    # PHQ-9 Assessment
    phq9, created = Assessment.objects.get_or_create(
        name='phq9',
        defaults={
            'title': 'PHQ-9 Depression Assessment',
            'description': 'Patient Health Questionnaire-9 for depression screening',
            'instructions': 'Over the last 2 weeks, how often have you been bothered by any of the following problems?'
        }
    )
    
    if created:
        phq9_questions = [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
            "Trouble falling or staying asleep, or sleeping too much",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself or that you are a failure or have let yourself or your family down",
            "Trouble concentrating on things, such as reading the newspaper or watching television",
            "Moving or speaking so slowly that other people could have noticed. Or the opposite being so fidgety or restless that you have been moving around a lot more than usual",
            "Thoughts that you would be better off dead, or of hurting yourself"
        ]
        
        for i, question_text in enumerate(phq9_questions):
            question = Question.objects.create(
                assessment=phq9,
                text=question_text,
                order=i+1
            )
            
            choices = [
                ("Not at all", 0),
                ("Several days", 1),
                ("More than half the days", 2),
                ("Nearly every day", 3)
            ]
            
            for j, (choice_text, value) in enumerate(choices):
                AnswerChoice.objects.create(
                    question=question,
                    text=choice_text,
                    value=value,
                    order=j+1
                )
    
    # GAD-7 Assessment
    gad7, created = Assessment.objects.get_or_create(
        name='gad7',
        defaults={
            'title': 'GAD-7 Anxiety Assessment',
            'description': 'Generalized Anxiety Disorder 7-item scale',
            'instructions': 'Over the last 2 weeks, how often have you been bothered by the following problems?'
        }
    )
    
    if created:
        gad7_questions = [
            "Feeling nervous, anxious, or on edge",
            "Not being able to stop or control worrying",
            "Worrying too much about different things",
            "Trouble relaxing",
            "Being so restless that it is hard to sit still",
            "Becoming easily annoyed or irritable",
            "Feeling afraid, as if something awful might happen"
        ]
        
        for i, question_text in enumerate(gad7_questions):
            question = Question.objects.create(
                assessment=gad7,
                text=question_text,
                order=i+1
            )
            
            choices = [
                ("Not at all", 0),
                ("Several days", 1),
                ("More than half the days", 2),
                ("Nearly every day", 3)
            ]
            
            for j, (choice_text, value) in enumerate(choices):
                AnswerChoice.objects.create(
                    question=question,
                    text=choice_text,
                    value=value,
                    order=j+1
                )
    
    # Create sample assessment results
    print("Creating sample assessment results...")
    users = User.objects.filter(role='user')[:3]
    assessments = Assessment.objects.all()
    
    for user in users:
        for assessment in assessments:
            user_assessment = UserAssessment.objects.create(
                user=user,
                assessment=assessment,
                total_score=random.randint(0, 20),
                is_completed=True,
                completed_at=timezone.now() - timedelta(days=random.randint(1, 30))
            )
            
            # Create a result
            score = user_assessment.total_score
            if assessment.name == 'phq9':
                if score < 5: severity = 'minimal'
                elif score < 10: severity = 'mild'
                elif score < 15: severity = 'moderate'
                elif score < 20: severity = 'moderately_severe'
                else: severity = 'severe'
            else:  # GAD-7
                if score < 5: severity = 'minimal'
                elif score < 10: severity = 'mild'
                elif score < 15: severity = 'moderate'
                else: severity = 'severe'
            
            AssessmentResult.objects.create(
                user_assessment=user_assessment,
                severity_level=severity,
                score_range=f"{score}",
                recommendation=f"Based on your score of {score}, we recommend appropriate follow-up."
            )
    
    # Create resource categories
    print("Creating resource categories...")
    categories_data = [
        ("Crisis Support", "Immediate help and crisis intervention", "fas fa-phone", "#EF4444"),
        ("Therapy & Counseling", "Professional therapy services", "fas fa-user-md", "#3B82F6"),
        ("Self-Help Resources", "Tools for self-improvement", "fas fa-book", "#10B981"),
        ("Support Groups", "Community support and groups", "fas fa-users", "#8B5CF6"),
        ("Educational Materials", "Learning about mental health", "fas fa-graduation-cap", "#F59E0B")
    ]
    
    for name, desc, icon, color in categories_data:
        ResourceCategory.objects.get_or_create(
            name=name,
            defaults={
                'description': desc,
                'icon': icon,
                'color': color
            }
        )
    
    # Create sample mental health resources
    print("Creating mental health resources...")
    crisis_category = ResourceCategory.objects.get(name="Crisis Support")
    therapy_category = ResourceCategory.objects.get(name="Therapy & Counseling")
    
    resources_data = [
        ("National Crisis Hotline", "24/7 crisis support hotline", "hotline", crisis_category, "", "1-800-273-8255", True, True),
        ("Online Therapy Platform", "Professional online therapy sessions", "contact", therapy_category, "https://example-therapy.com", "", False, False),
        ("Mental Health First Aid", "Learn how to help someone in crisis", "article", crisis_category, "https://example-firstaid.com", "", True, False),
    ]
    
    for title, desc, res_type, category, url, phone, is_free, is_24_7 in resources_data:
        MentalHealthResource.objects.get_or_create(
            title=title,
            defaults={
                'description': desc,
                'resource_type': res_type,
                'category': category,
                'url': url,
                'phone_number': phone,
                'is_free': is_free,
                'is_24_7': is_24_7,
                'is_verified': True
            }
        )
    
    # Create sample professionals
    print("Creating sample professionals...")
    professionals_data = [
        ("Dr. Maria Santos", "clinical_psychologist", "Manila Psychology Clinic", "Makati City", "02-123-4567"),
        ("Dr. Juan Dela Cruz", "psychiatrist", "Mind Wellness Center", "Quezon City", "02-987-6543"),
        ("Sarah Johnson", "counselor", "Hope Counseling Services", "Pasig City", "02-555-0123"),
    ]
    
    for name, spec, clinic, city, phone in professionals_data:
        ProfessionalContact.objects.get_or_create(
            name=name,
            defaults={
                'specialization': spec,
                'clinic_name': clinic,
                'address': f"123 Health Street, {city}",
                'city': city,
                'phone': phone,
                'email': f"{name.lower().replace(' ', '').replace('.', '')}@example.com",
                'is_verified': True
            }
        )
    
    # Create sample exercises
    print("Creating sample exercises...")
    exercises_data = [
        ("Deep Breathing Exercise", "A simple breathing technique to reduce anxiety", "breathing", 
         "1. Sit comfortably\n2. Breathe in for 4 counts\n3. Hold for 4 counts\n4. Breathe out for 6 counts\n5. Repeat 5-10 times", 5),
        ("Progressive Muscle Relaxation", "Systematic tensing and relaxing of muscle groups", "progressive_relaxation",
         "1. Start with your toes\n2. Tense for 5 seconds\n3. Relax completely\n4. Move up through each muscle group\n5. End with your head and face", 15),
        ("Mindful Meditation", "Basic mindfulness meditation practice", "meditation",
         "1. Find a quiet space\n2. Sit comfortably\n3. Focus on your breath\n4. When mind wanders, gently return to breath\n5. Start with 5-10 minutes", 10),
    ]
    
    for title, desc, ex_type, instructions, duration in exercises_data:
        SelfHelpExercise.objects.get_or_create(
            title=title,
            defaults={
                'description': desc,
                'exercise_type': ex_type,
                'instructions': instructions,
                'duration_minutes': duration,
                'difficulty_level': 'beginner'
            }
        )
    
    print("Sample data created successfully!")
    print("\nYou can now:")
    print("1. Login as admin with your superuser credentials")
    print("2. Login as regular users: user1-user10 (password: password123)")
    print("3. Login as organizations: org1-org3 (password: password123)")
    print("4. Test the assessments, mood tracking, and other features")

if __name__ == "__main__":
    create_sample_data()
