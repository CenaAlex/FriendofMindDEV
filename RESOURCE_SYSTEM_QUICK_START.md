# Resource Management System - Quick Start Guide

## 🚀 Quick Access

### For Regular Users
- **Browse Resources**: `/resources/` or click "Resources" in the navigation menu
- **My Bookmarks**: `/resources/my-bookmarks/` or click button on resources page
- **View Resource**: Click "View Details" on any resource card
- **Report Issue**: Click "Report Issue" on resource detail page

### For Admins
- **Manage Resources**: Admin Dashboard → "Manage Resources" 
  - Or directly at: `/resources/admin/resources/`
- **Create Resource**: Manage Resources page → "Add New Resource" button
- **Edit Resource**: Manage Resources page → Edit icon (pencil)
- **Delete Resource**: Manage Resources page → Delete icon (trash)

---

## 👤 Regular User Features

### 1. Browse & Access Resources
**Steps:**
1. Click "Resources" in navigation menu
2. Browse all resources or filter by category
3. Click "View Details" to see full information
4. Access contact info (phone, email, website)

### 2. Bookmark Resources
**Steps:**
1. Go to a resource detail page
2. Click the "Bookmark" button (top right)
3. Button turns yellow → Resource is bookmarked ✅
4. Click again to unbookmark

**View All Bookmarks:**
- Click "My Bookmarks" button on resources page
- Or go to `/resources/my-bookmarks/`
- Remove bookmarks by clicking trash icon

### 3. Report Inaccurate Information
**Steps:**
1. Go to resource detail page
2. Click "Report Issue" button (bottom)
3. Fill out issue description
4. Click "Submit Report"
5. Confirmation message appears
6. Admin reviews and responds via notifications

**Report Goes To:**
- Admin's Feedback Management page
- Type: "Issue"
- Subject: "Resource Issue Report: [Resource Title]"
- Contains full resource details + your description

---

## 👨‍💼 Admin Features

### 1. View All Resources
**Steps:**
1. Go to Admin Dashboard
2. Click "Manage Resources" in System Management section
3. View all resources in table format

**Features:**
- Statistics at top (total, active, inactive)
- Filter by: search, category, type, status
- Sort by creation date
- Pagination (20 per page)

### 2. Create New Resource
**Steps:**
1. Go to Manage Resources page
2. Click "Add New Resource" (green button, top right)
3. Fill out the form:
   - **Basic Info**: Title, Description, Type, Category
   - **Contact Info**: URL, Phone, Email, Address (at least one required)
   - **Details**: Languages, Free?, 24/7?, Verified?, Active?
4. Click "Create Resource"
5. Success message appears
6. Resource is now visible to users (if active)

**Resource Types:**
- Article
- Video
- Hotline
- App
- Website
- Exercise
- Meditation
- Book

### 3. Edit Resource
**Steps:**
1. Go to Manage Resources page
2. Find resource (use filters if needed)
3. Click edit icon (green pencil)
4. Update any fields
5. Click "Update Resource"
6. Changes saved ✅

### 4. Delete Resource
**Steps:**
1. Go to Manage Resources page
2. Click delete icon (red trash)
3. Review warning page
4. Click "Yes, Delete Resource"
5. Resource and all bookmarks removed

**Warning:**
- Action cannot be undone
- All user bookmarks will be removed
- All view history will be deleted

### 5. Toggle Resource Status
**Quick Method:**
1. Go to Manage Resources page
2. Click power icon (orange/green)
3. Confirm
4. Status instantly toggled

**What It Does:**
- Active → Inactive: Users can't see it anymore
- Inactive → Active: Users can see it again
- Useful for temporary issues or updates

### 6. Handle Resource Reports
**Steps:**
1. Go to "Feedback Management" from Admin Dashboard
2. Filter by Type: "Issue"
3. Look for "Resource Issue Report: [Title]"
4. Click to view details
5. Review the issue description
6. Take action:
   - Edit the resource to fix issue
   - Deactivate if serious problem
   - Delete if inappropriate
7. Respond to user via feedback response
8. Mark as "Resolved"

**Report Contains:**
- Resource ID
- Resource Title
- Resource Type
- Category
- User's issue description

---

## 🎯 Common Tasks

### Task: Add a New Crisis Hotline
```
1. Admin Dashboard → Manage Resources
2. Add New Resource
3. Fill out:
   - Title: "National Suicide Prevention Lifeline"
   - Description: "24/7 confidential support..."
   - Type: Hotline
   - Category: Crisis Support
   - Phone: 988
   - Free: ✅ Yes
   - 24/7: ✅ Yes
   - Verified: ✅ Yes
   - Active: ✅ Yes
4. Create Resource
```

### Task: Add an Article Resource
```
1. Admin Dashboard → Manage Resources
2. Add New Resource
3. Fill out:
   - Title: "Understanding Anxiety"
   - Description: "Comprehensive guide to..."
   - Type: Article
   - Category: Self-Help
   - URL: https://example.com/anxiety-guide
   - Free: ✅ Yes
   - Active: ✅ Yes
4. Create Resource
```

### Task: User Reports Wrong Phone Number
```
As User:
1. View resource → Report Issue
2. Describe: "Phone number is disconnected"
3. Submit

As Admin:
1. Feedback Management → Issues
2. Find report
3. Edit resource → Update phone number
4. Respond: "Thank you! Phone number updated."
5. Mark as Resolved
```

### Task: Temporarily Hide Resource for Updates
```
1. Manage Resources
2. Find resource
3. Click power icon (toggle)
4. Resource now inactive (users can't see)
5. Edit resource → Make updates
6. Click power icon again
7. Resource active again ✅
```

---

## 📊 Admin Filters

### Search
- Searches in title and description
- Example: Search "anxiety" finds all anxiety-related resources

### Category Filter
- Crisis Support
- Therapy Resources
- Self-Help Materials
- Support Groups
- Emergency Services
- Educational Content

### Type Filter
- Article
- Video
- Hotline
- App
- Website
- Exercise
- Meditation
- Book

### Status Filter
- All (default)
- Active (visible to users)
- Inactive (hidden from users)

---

## 🎨 UI Elements Guide

### Resource Detail Page
```
┌─────────────────────────────────────┐
│ [Resource Title]        [Bookmark] │
│ Type | Category | Free | 24/7      │
│                                     │
│ About This Resource                 │
│ [Description text...]               │
│                                     │
│ Contact Information                 │
│ 🌐 Website                         │
│ 📞 Phone                           │
│ 📧 Email                           │
│                                     │
│ [Back] [Report Issue]              │
└─────────────────────────────────────┘
```

### Admin Resource List
```
┌─────────────────────────────────────┐
│ Resource Management  [+ Add New]    │
│                                     │
│ Stats: Total | Active | Inactive    │
│                                     │
│ Filters: [Search] [Category] [Type] │
│                                     │
│ Table:                              │
│ Title | Type | Category | Status    │
│ Actions: 👁 ✏️ ⚡ 🗑              │
└─────────────────────────────────────┘
```

---

## ✅ Testing Checklist

### User Testing
- [ ] Can browse resources
- [ ] Can view resource details
- [ ] Can bookmark a resource
- [ ] Bookmark button turns yellow
- [ ] Can view bookmarks page
- [ ] Can unbookmark from detail page
- [ ] Can unbookmark from bookmarks page
- [ ] Can report a resource
- [ ] Report submits successfully
- [ ] Receives confirmation message

### Admin Testing
- [ ] Can access Manage Resources
- [ ] Can view all resources
- [ ] Statistics display correctly
- [ ] Can filter by search
- [ ] Can filter by category
- [ ] Can filter by type
- [ ] Can filter by status
- [ ] Can create new resource
- [ ] Can edit existing resource
- [ ] Can delete resource
- [ ] Can toggle status
- [ ] Reports appear in Feedback Management
- [ ] Can respond to reports

---

## 🚨 Troubleshooting

### Issue: Can't see resources
**Solution:**
- Make sure resources are marked as "Active"
- Check if category is active
- Admin can see inactive resources, users cannot

### Issue: Bookmark button not working
**Solution:**
- Make sure JavaScript is enabled
- Check browser console for errors
- Try refreshing the page
- Make sure you're logged in

### Issue: Report not showing in Feedback Management
**Solution:**
- Go to Feedback Management
- Make sure filter is not excluding "issue" type
- Reports might be on another page (check pagination)
- Subject starts with "Resource Issue Report:"

### Issue: Can't access admin pages
**Solution:**
- Make sure you're logged in as admin (staff or superuser)
- Check user.is_staff or user.is_superuser is True
- Contact system administrator

---

## 📞 Key URLs Reference

```
User URLs:
/resources/                                   - Browse resources
/resources/category/<id>/                     - Filter by category
/resources/resource/<id>/                     - View details
/resources/my-bookmarks/                      - My bookmarks
/resources/report/<id>/                       - Report issue

Admin URLs:
/resources/admin/resources/                   - Manage all
/resources/admin/resource/create/             - Create new
/resources/admin/resource/<id>/edit/          - Edit
/resources/admin/resource/<id>/delete/        - Delete
```

---

## 🎉 Quick Tips

### For Users:
💡 **Bookmark resources you might need later** - Access them quickly from My Bookmarks
💡 **Report issues to help others** - Your reports improve the system for everyone
💡 **Check back regularly** - New resources are added by admins

### For Admins:
💡 **Keep resources up-to-date** - Verify contact info regularly
💡 **Respond to reports quickly** - Users appreciate fast resolution
💡 **Use inactive status** - For resources under review, not permanent deletion
💡 **Add detailed descriptions** - Help users understand what the resource offers
💡 **Verify trustworthy resources** - Use the "Verified" checkbox for quality control

---

## 🎯 Next Steps

1. **Test the system** - Try all features as both user and admin
2. **Add initial resources** - Populate with quality mental health resources
3. **Train admins** - Share this guide with admin team
4. **Announce to users** - Let users know about the new features
5. **Monitor feedback** - Check reports and user engagement
6. **Iterate** - Improve based on user feedback

---

Need help? All features are documented in `RESOURCE_MANAGEMENT_SYSTEM.md`! 📚

