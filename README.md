# FriendofMind - Mental Health Support Platform

A comprehensive mental health screening and support platform designed specifically for Filipino individuals seeking accessible early mental health guidance and resources.

## Features

### 🔍 Mental Health Assessments
- **PHQ-9 Depression Screening**: 9-question validated assessment for depression symptoms
- **GAD-7 Anxiety Screening**: 7-question assessment for generalized anxiety disorder  
- **PSS (Perceived Stress Scale)**: 10-question assessment for stress levels
- Automated scoring and severity level classification
- Personalized recommendations based on results

### 📊 User Dashboard
- Progress tracking and mood history
- Quick access to assessments and resources
- Personal statistics and insights
- Mood logging functionality

### 🏥 Professional Directory
- Verified mental health professionals across the Philippines
- Detailed profiles with specializations, contact info, and fees
- Search and filter by location, specialty, and availability
- Telehealth options available

### 📚 Resource Library
- Categorized mental health resources
- Crisis support hotlines (988, Crisis Text Line)
- Self-help articles and guides
- Educational materials and exercises

### 🧘 Self-Help Exercises
- Guided breathing exercises (4-7-8 technique)
- Progressive muscle relaxation
- Grounding techniques (5-4-3-2-1)
- Gratitude journaling prompts
- Mindfulness and meditation guides

## Technology Stack

- **Backend**: Django 5.2.6 (Python)
- **Frontend**: HTML5 + Tailwind CSS
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Authentication**: Django built-in user management
- **UI Framework**: Tailwind CSS with responsive design

## Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Clone and setup**:
   ```bash
   cd C:\Users\Stephanie\Desktop\FriendOfMind
   # Virtual environment is already set up
   ```

2. **Install dependencies**:
   ```bash
   pip install django psycopg2-binary pillow
   ```

3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Populate sample data**:
   ```bash
   python populate_data.py
   ```

5. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the application**:
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## User Guide

### For Users
1. **Register**: Create an account with basic information
2. **Take Assessments**: Complete PHQ-9, GAD-7, or PSS screenings
3. **View Results**: Get instant feedback and recommendations
4. **Track Progress**: Log daily moods and monitor trends
5. **Find Help**: Browse professional directory and resources
6. **Self-Care**: Access guided exercises and educational content

### For Administrators
1. **Access Admin Panel**: Login at `/admin/` with superuser credentials
2. **Manage Resources**: Add/edit mental health resources and professionals
3. **Monitor Assessments**: View user assessment results and trends
4. **Content Management**: Update educational materials and exercises

## Database Models

### Core Models
- **User**: Extended Django user with mental health specific fields
- **UserProfile**: Additional user preferences and settings
- **MoodEntry**: Daily mood tracking entries

### Assessment Models
- **Assessment**: Mental health screening tools (PHQ-9, GAD-7, PSS)
- **Question**: Individual assessment questions
- **AnswerChoice**: Multiple choice options with scoring
- **UserAssessment**: User's assessment attempts and scores
- **AssessmentResult**: Detailed results with severity and recommendations

### Resource Models
- **ResourceCategory**: Organization categories for mental health resources
- **MentalHealthResource**: Articles, hotlines, and educational materials
- **ProfessionalContact**: Licensed mental health professionals
- **SelfHelpExercise**: Guided self-care activities

## Security & Privacy

- All user data is encrypted and secure
- Assessment results are confidential
- No personal information is shared without consent
- Crisis detection with immediate resource recommendations
- HIPAA-compliant data handling practices

## Crisis Support

**Immediate Help Available 24/7:**
- National Suicide Prevention Lifeline: **988**
- Crisis Text Line: Text HOME to **741741** 
- SAMHSA National Helpline: **1-800-662-4357**

## Scope & Limitations

### Scope
- Filipino users (students, young professionals, adults)
- Mild to moderate mental health concerns
- Early intervention and awareness
- Educational and supportive resources
- Connection to professional help

### Limitations
- Not a replacement for professional diagnosis or treatment
- Limited to initial screening and awareness
- Does not provide long-term clinical outcome tracking
- Focused on Filipino context and may not apply to other cultures
- Evaluation based on short-term user feedback

## Future Enhancements

- Real-time analytics and reporting
- Mobile app development
- Multilingual support (Filipino, Cebuano, etc.)
- Integration with telehealth platforms
- AI-powered chatbot support
- Extended assessment tools
- Community support features

## Contributing

This platform is developed as part of a research study on digital mental health support for Filipino individuals. For questions or collaboration opportunities, please contact the development team.

## License

This project is developed for educational and research purposes. All mental health assessment tools used are validated instruments available in the public domain.

## Disclaimer

This platform is for informational and educational purposes only. It is not intended to diagnose, treat, cure, or prevent any mental health condition. Always consult with qualified mental health professionals for proper diagnosis and treatment. In case of emergency, contact local emergency services or crisis hotlines immediately.