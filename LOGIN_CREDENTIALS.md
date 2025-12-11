# Login Credentials for Testing

## 🔐 Test Accounts

### Admin Account (Superuser)
```
Username: admin
Password: admin123
Email: admin@friendofmind.com
Role: Admin/Superuser
Access: Full system access, can manage everything
```

**What Admin Can Do:**
- ✅ Manage all users and organizations
- ✅ View platform-wide analytics
- ✅ Manage assessments (create, edit, delete)
- ✅ Moderate forum posts
- ✅ Manage feedback and respond to users
- ✅ View all resources and create new ones
- ✅ View mood analytics for all users
- ❌ Cannot take assessments (blocked)
- ❌ Cannot log mood entries (admin exclusion)

---

### Regular User Accounts

#### User 1: Stan
```
Username: Stan
Password: user123
Email: munasquestanlee@gmail.com
Role: Regular User
Access: Standard user features
```

#### User 2: alex
```
Username: alex
Password: user123
Email: test@gmail.com
Role: Regular User
Access: Standard user features
```

**What Regular Users Can Do:**
- ✅ Take mental health assessments (PHQ-9, GAD-7, PSS)
- ✅ Log mood entries daily
- ✅ View their mood history and insights
- ✅ Post in community forum
- ✅ Like, comment, and report forum posts
- ✅ Access and bookmark resources
- ✅ Report inaccurate resource information
- ✅ Submit feedback to admin
- ✅ View notifications
- ❌ Cannot access admin features
- ❌ Cannot manage other users

---

### Organization Accounts

#### Organization 1: alexes
```
Username: alexes
Password: (not set yet)
Email: alexes@gmail.com
Role: Organization
```

#### Organization 2: Friend
```
Username: Friend
Password: (not set yet)
Email: (none)
Role: Organization
```

**Note:** Organization accounts have different dashboard and features. If you need to test these, I can set passwords for them too.

---

## 🚀 How to Login

### Step 1: Go to Login Page
- Visit: `http://127.0.0.1:8000/`
- Or click "Sign In" button

### Step 2: Enter Credentials
- **For Admin Testing:**
  - Username: `admin`
  - Password: `admin123`

- **For User Testing:**
  - Username: `Stan` or `alex`
  - Password: `user123`

### Step 3: Click "Sign In"

---

## 🧪 Testing Scenarios

### Test Admin Features:
1. Login as **admin** (admin/admin123)
2. Go to Admin Dashboard
3. Test:
   - User management
   - Assessment management
   - Forum moderation
   - Feedback responses
   - Mood analytics
   - Resource management

### Test User Features:
1. Login as **Stan** (Stan/user123)
2. Test:
   - Take an assessment
   - Log mood entry (popup should appear)
   - Browse and bookmark resources
   - Post in forum
   - Submit feedback
   - View mood history

### Test Both Accounts:
1. Login as **Stan** → Post in forum → Submit feedback
2. Logout
3. Login as **admin** → See notification → Respond to feedback → Moderate forum
4. Logout
5. Login as **Stan** → See response notification

---

## 🔄 Reset Passwords

If you need to change passwords or set new ones, use:

```bash
python manage.py shell -c "from core.models import User; u = User.objects.get(username='USERNAME'); u.set_password('NEWPASSWORD'); u.save(); print('Password updated!')"
```

Replace `USERNAME` and `NEWPASSWORD` with desired values.

---

## 📝 Create New Test User

To create a brand new test user:

```bash
python manage.py shell -c "from core.models import User; User.objects.create_user(username='testuser', email='test@test.com', password='test123', role='user'); print('User created!')"
```

---

## ⚠️ Important Notes

1. **These are test credentials** - Don't use in production!
2. **Admin cannot take assessments** - Use regular user account for that
3. **Mood tracker only for users** - Admin won't see the popup
4. **Organization accounts** - Have different dashboard layout
5. **Active status** - All accounts are active and can login

---

## 🎯 Quick Reference

| Account | Username | Password | Purpose |
|---------|----------|----------|---------|
| Admin | `admin` | `admin123` | Test admin features |
| User 1 | `Stan` | `user123` | Test user features |
| User 2 | `alex` | `user123` | Test user features |
| Org 1 | `alexes` | (not set) | Organization testing |
| Org 2 | `Friend` | (not set) | Organization testing |

---

Happy Testing! 🚀



