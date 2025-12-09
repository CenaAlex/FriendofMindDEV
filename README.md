# FriendOfMind - Mental Health Platform

A Django-based mental health platform for mood tracking, assessments, resources, and community support.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Setup Instructions

### 1. Create a Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

The project uses SQLite (no additional database server needed). Run migrations to create the database:

```bash
python manage.py makemigrations
python manage.py migrate
```

This will create a `db.sqlite3` file in the project root with all the necessary tables.

### 4. Create a Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account. You'll need this to access the Django admin panel.

### 5. Collect Static Files (Optional, for production)

```bash
python manage.py collectstatic
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

- Admin panel: **http://127.0.0.1:8000/admin/**
- Landing page: **http://127.0.0.1:8000/**

## Database Information

- **Database Type**: SQLite3
- **Database File**: `db.sqlite3` (created automatically after migrations)
- **Location**: Project root directory

The database file is already in `.gitignore`, so it won't be committed to version control. Each developer/environment will have their own local database.

## Project Structure

- `core/` - Main application with user management, mood tracking, forums, feedback
- `assessments/` - Assessment management
- `mentalhealth/` - Mental health resources
- `resources/` - Resource management
- `screening/` - Screening tools
- `templates/` - HTML templates
- `friendofmind/` - Project settings and configuration

## Common Commands

```bash
# Run migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Access Django shell
python manage.py shell

# Run tests
python manage.py test
```

## Troubleshooting

- **ImportError**: Make sure your virtual environment is activated
- **Database errors**: Run `python manage.py migrate` to apply migrations
- **Static files not loading**: Run `python manage.py collectstatic`
- **Port already in use**: Use `python manage.py runserver 8001` to use a different port





