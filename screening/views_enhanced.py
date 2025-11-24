"""
Enhanced Assessment Views - One Question at a Time with Navigation
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models import Assessment, UserAssessment, Question, AnswerChoice, UserAnswer, AssessmentResult


@login_required
def start_assessment(request, assessment_type):
    """Start a new assessment - creates UserAssessment and redirects to first question"""
    # Block admins
    if request.user.is_superuser or request.user.is_staff:
        messages.warning(request, 'Admins cannot take assessments.')
        return redirect('core:admin_dashboard')
    
    # Get assessment (filter by name AND is_active, get first to avoid MultipleObjectsReturned)
    assessment = Assessment.objects.filter(
        name=assessment_type,
        is_active=True
    ).order_by('-created_at').first()
    
    if not assessment:
        messages.error(request, 'Assessment not found.')
        return redirect('screening:assessment_list')
    
    # Check if user already has an incomplete assessment
    incomplete = UserAssessment.objects.filter(
        user=request.user,
        assessment=assessment,
        is_completed=False
    ).first()
    
    if incomplete:
        # Continue from where they left off
        answered_count = UserAnswer.objects.filter(user_assessment=incomplete).count()
        next_question_number = answered_count + 1
        return redirect('screening:take_assessment_question', 
                       assessment_id=incomplete.id, 
                       question_number=next_question_number)
    
    # Create new user assessment
    user_assessment = UserAssessment.objects.create(
        user=request.user,
        assessment=assessment,
        is_completed=False
    )
    
    # Start at question 1
    return redirect('screening:take_assessment_question', 
                   assessment_id=user_assessment.id, 
                   question_number=1)


@login_required
def take_assessment_question(request, assessment_id, question_number):
    """Display and process one question at a time"""
    # Get user assessment
    user_assessment = get_object_or_404(
        UserAssessment, 
        id=assessment_id, 
        user=request.user
    )
    
    # Block if already completed
    if user_assessment.is_completed:
        messages.info(request, 'This assessment is already completed.')
        return redirect('screening:assessment_result', assessment_id=user_assessment.id)
    
    # Get all questions for this assessment (ordered)
    questions = list(user_assessment.assessment.questions.all().order_by('order'))
    total_questions = len(questions)
    
    # Validate question number
    if question_number < 1 or question_number > total_questions:
        messages.error(request, 'Invalid question number.')
        return redirect('screening:start_assessment', 
                       assessment_type=user_assessment.assessment.name)
    
    # Get current question
    current_question = questions[question_number - 1]
    
    # Get existing answer for this question (if any)
    existing_answer = UserAnswer.objects.filter(
        user_assessment=user_assessment,
        question=current_question
    ).first()
    
    if request.method == 'POST':
        print(f"DEBUG: POST received - Action: {request.POST.get('action')}, Answer: {request.POST.get('answer')}")
        action = request.POST.get('action')
        
        if action == 'next' or action == 'submit':
            # Save answer
            answer_id = request.POST.get('answer')
            
            if not answer_id:
                print(f"DEBUG: No answer selected")
                messages.error(request, 'Please select an answer.')
                return redirect('screening:take_assessment_question', 
                               assessment_id=assessment_id, 
                               question_number=question_number)
            
            answer_choice = get_object_or_404(AnswerChoice, id=answer_id)
            print(f"DEBUG: Answer choice found: {answer_choice.text}")
            
            # Update or create answer
            if existing_answer:
                existing_answer.answer_choice = answer_choice
                existing_answer.save()
                print(f"DEBUG: Updated existing answer")
            else:
                UserAnswer.objects.create(
                    user_assessment=user_assessment,
                    question=current_question,
                    answer_choice=answer_choice
                )
                print(f"DEBUG: Created new answer")
            
            # Check if this was the last question
            if question_number == total_questions:
                print(f"DEBUG: Last question - completing assessment")
                # Complete the assessment
                return complete_assessment(request, user_assessment)
            else:
                print(f"DEBUG: Going to next question: {question_number + 1}")
                # Go to next question
                return redirect('screening:take_assessment_question', 
                               assessment_id=assessment_id, 
                               question_number=question_number + 1)
        
        elif action == 'back':
            print(f"DEBUG: Going back to question: {question_number - 1}")
            # Go to previous question
            if question_number > 1:
                return redirect('screening:take_assessment_question', 
                               assessment_id=assessment_id, 
                               question_number=question_number - 1)
    
    # Calculate progress
    answered_count = UserAnswer.objects.filter(user_assessment=user_assessment).count()
    progress_percentage = (answered_count / total_questions) * 100
    
    context = {
        'user_assessment': user_assessment,
        'assessment': user_assessment.assessment,
        'question': current_question,
        'question_number': question_number,
        'total_questions': total_questions,
        'is_first_question': question_number == 1,
        'is_last_question': question_number == total_questions,
        'progress_percentage': round(progress_percentage),
        'existing_answer': existing_answer,
    }
    
    return render(request, 'screening/take_assessment_enhanced.html', context)


def complete_assessment(request, user_assessment):
    """Calculate score and create result"""
    # Calculate total score
    answers = UserAnswer.objects.filter(user_assessment=user_assessment)
    total_score = sum(answer.answer_choice.value for answer in answers)
    
    # Update user assessment
    user_assessment.total_score = total_score
    user_assessment.is_completed = True
    user_assessment.save()
    
    # Calculate severity and create result
    severity_level = calculate_severity(user_assessment.assessment.name, total_score)
    recommendation = get_recommendation(severity_level)
    
    AssessmentResult.objects.create(
        user_assessment=user_assessment,
        severity_level=severity_level,
        score_range=f"{total_score}",
        recommendation=recommendation
    )
    
    messages.success(request, 'Assessment completed successfully!')
    return redirect('screening:assessment_result', assessment_id=user_assessment.id)


def calculate_severity(assessment_name, score):
    """Calculate severity level based on assessment type and score"""
    if assessment_name == 'phq9':
        if score < 5: return 'minimal'
        elif score < 10: return 'mild'
        elif score < 15: return 'moderate'
        elif score < 20: return 'moderately_severe'
        else: return 'severe'
    elif assessment_name == 'gad7':
        if score < 5: return 'minimal'
        elif score < 10: return 'mild'
        elif score < 15: return 'moderate'
        else: return 'severe'
    elif assessment_name == 'pss':
        if score < 14: return 'minimal'
        elif score < 27: return 'mild'
        elif score < 41: return 'moderate'
        else: return 'severe'
    else:
        # Generic scoring
        if score < 10: return 'minimal'
        elif score < 20: return 'mild'
        elif score < 30: return 'moderate'
        else: return 'severe'


def get_recommendation(severity_level):
    """Get recommendation text based on severity"""
    recommendations = {
        'minimal': 'Your scores suggest minimal symptoms. Continue with self-care practices and maintain your mental wellness routine.',
        'mild': 'Your scores suggest mild symptoms. Consider speaking with a mental health professional and explore our self-help resources.',
        'moderate': 'Your scores suggest moderate symptoms. We recommend consulting with a mental health professional for further evaluation and support.',
        'moderately_severe': 'Your scores suggest moderately severe symptoms. Please consider seeking professional help soon. Your symptoms may benefit from treatment.',
        'severe': 'Your scores suggest severe symptoms. We strongly recommend seeking immediate professional help. Please consider contacting a mental health provider or crisis line.'
    }
    return recommendations.get(severity_level, 'Please consult with a mental health professional for personalized guidance.')

