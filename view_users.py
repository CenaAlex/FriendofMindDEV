#!/usr/bin/env python
"""
Quick script to view all users in the database
Run: python view_users.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'friendofmind.settings')
django.setup()

from core.models import User

print("=" * 80)
print("USERS IN DATABASE")
print("=" * 80)
print()

users = User.objects.all().order_by('-date_joined')

if not users.exists():
    print("No users found in the database.")
else:
    print(f"Total users: {users.count()}\n")
    print(f"{'Username':<20} {'Email':<30} {'Role':<15} {'Active':<8} {'Staff':<8} {'Joined':<20}")
    print("-" * 80)
    
    for user in users:
        print(f"{user.username:<20} {user.email or 'N/A':<30} {user.role:<15} "
              f"{'Yes' if user.is_active else 'No':<8} {'Yes' if user.is_staff else 'No':<8} "
              f"{user.date_joined.strftime('%Y-%m-%d %H:%M'):<20}")
    
    print()
    print("=" * 80)
    print("\nUser Details:")
    print("-" * 80)
    
    for user in users:
        print(f"\nUsername: {user.username}")
        print(f"  Email: {user.email or 'N/A'}")
        print(f"  Name: {user.get_full_name() or 'N/A'}")
        print(f"  Role: {user.role}")
        print(f"  Active: {user.is_active}")
        print(f"  Staff: {user.is_staff}")
        print(f"  Superuser: {user.is_superuser}")
        print(f"  Joined: {user.date_joined}")
        if user.phone:
            print(f"  Phone: {user.phone}")





