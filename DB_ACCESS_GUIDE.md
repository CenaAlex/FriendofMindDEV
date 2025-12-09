# Database Access Guide

## Method 1: Django Admin Panel (Easiest - Visual Interface)

1. Start the server:
   ```bash
   python manage.py runserver
   ```

2. Open browser: http://127.0.0.1:8000/admin/

3. Login with superuser credentials

4. Click on "Users" to see all users with filtering and search options

---

## Method 2: Quick Python Script

Run the provided script:
```bash
python view_users.py
```

This shows all users in a formatted table.

---

## Method 3: Django Shell (Interactive)

Open Django shell:
```bash
python manage.py shell
```

Then run these commands:

```python
# Import User model
from core.models import User

# Get all users
users = User.objects.all()
print(f"Total users: {users.count()}")

# List all usernames
for user in users:
    print(f"{user.username} - {user.email} - {user.role}")

# Get specific user
user = User.objects.get(username='admin')
print(user.email)

# Filter users
active_users = User.objects.filter(is_active=True)
regular_users = User.objects.filter(role='user')
org_users = User.objects.filter(role='organization')

# Search users
search = User.objects.filter(username__icontains='alex')
```

---

## Method 4: SQLite Command Line

Direct SQLite access:

```bash
# Open SQLite database
sqlite3 db.sqlite3

# Then run SQL queries:
.tables                    # List all tables
.schema core_user          # Show user table structure

# Query users
SELECT username, email, role, is_active FROM core_user;

# Count users
SELECT COUNT(*) FROM core_user;

# Exit
.quit
```

---

## Method 5: Database Browser Tools (GUI)

Use a SQLite browser tool:

**DB Browser for SQLite** (Free):
- Download: https://sqlitebrowser.org/
- Open `db.sqlite3` file
- Browse tables visually
- Run SQL queries

**VS Code Extension**:
- Install "SQLite Viewer" extension
- Right-click `db.sqlite3` → "Open Database"

---

## Quick User Queries (Django Shell)

```python
# Count users by role
from core.models import User
from django.db.models import Count

User.objects.values('role').annotate(count=Count('id'))

# Get active users
User.objects.filter(is_active=True).count()

# Get users created in last 30 days
from django.utils import timezone
from datetime import timedelta

recent = User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=30))
print(f"Users created in last 30 days: {recent.count()}")

# Get superusers
User.objects.filter(is_superuser=True)

# Export users to list
users_list = list(User.objects.values('username', 'email', 'role', 'is_active'))
print(users_list)
```

---

## Current Database Status

- **Database File**: `db.sqlite3`
- **Location**: Project root directory
- **Type**: SQLite3 (file-based, no server needed)





