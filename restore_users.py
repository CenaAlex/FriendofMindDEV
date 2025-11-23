"""
Script to restore original test users
"""
from core.models import User

print("Creating/Restoring Test Users...")

# Create admin1
try:
    admin = User.objects.get(username='admin1')
    admin.set_password('admin123')
    admin.is_superuser = True
    admin.is_staff = True
    admin.is_active = True
    admin.email = 'admin1@friendofmind.com'
    admin.save()
    print("✅ Admin1 password reset")
except User.DoesNotExist:
    admin = User.objects.create_superuser(
        username='admin1',
        email='admin1@friendofmind.com',
        password='admin123',
        role='user'
    )
    print("✅ Admin1 created")

# Create user1-user10
for i in range(1, 11):
    username = f'user{i}'
    try:
        user = User.objects.get(username=username)
        user.set_password('password123')
        user.is_active = True
        user.role = 'user'
        user.email = f'user{i}@test.com'
        user.save()
        print(f"✅ {username} password reset")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email=f'user{i}@test.com',
            password='password123',
            role='user'
        )
        print(f"✅ {username} created")

print("\n✅ All users restored!")
print("\nLogin Credentials:")
print("=" * 50)
print("Admin:")
print("  Username: admin1")
print("  Password: admin123")
print("\nRegular Users:")
for i in range(1, 11):
    print(f"  user{i} / password123")

