# Analytics Page Fix - Dynamic Data

## 🐛 Problem

The Analytics & Reports page was showing blank/empty data for several sections:
- ❌ Organizations count showing blank
- ❌ User Growth chart empty
- ❌ Assessment Types showing "No assessment data available"
- ❌ Organization Types showing "No organization data available"

**Root Cause:** The analytics view wasn't passing the correct data to the template. Template was looking for variables that didn't exist in the context.

---

## ✅ What Was Fixed

### 1. **Variable Name Mismatches**

**Problems:**
- Template wanted `total_organizations` but view only passed `organizations` (count of org users, not orgs)
- Template wanted `monthly_users` but view passed `monthly_data`
- Template wanted `assessment_types` but view passed `assessment_breakdown`
- Template wanted `org_types` but view didn't pass it at all

**Fixed:**
```python
# Now passing correct variables:
context['total_organizations'] = Organization.objects.count()  # Actual org count
context['monthly_users'] = monthly_users  # Monthly user growth data
context['assessment_types'] = {...}  # Assessment breakdown by type
context['org_types'] = {...}  # Organization types breakdown
```

### 2. **Organization Count Fixed**
```python
# BEFORE (Wrong):
context['organizations'] = User.objects.filter(role='organization').count()
# This counts users with role='organization', not Organization objects!

# AFTER (Correct):
context['total_organizations'] = Organization.objects.count()
# Now counts actual Organization model instances
```

### 3. **Monthly User Growth Fixed**
```python
# BEFORE:
- Used 'date_joined' field (doesn't exist on custom User model)
- Returned as 'monthly_data' (template expects 'monthly_users')

# AFTER:
- Uses 'created_at' field (correct for custom User model)
- Returns as 'monthly_users' (matches template)
- Properly formatted: OrderedDict with month names as keys
- Last 12 months from oldest to newest
```

### 4. **Assessment Types Data Fixed**
```python
# BEFORE:
context['assessment_breakdown'] = {...}  # Wrong variable name!

# AFTER:
context['assessment_types'] = {...}  # Correct! Matches template
```

### 5. **Organization Types Added**
```python
# BEFORE:
# Not included at all!

# AFTER:
org_types = Organization.objects.values('organization_type').annotate(
    count=Count('id')
).order_by('-count')
context['org_types'] = {item['organization_type']: item['count'] for item in org_types}
```

---

## 📊 What Analytics Now Shows

### **Overview Stats (Top Cards):**
- ✅ **Total Users**: Count of all User objects
- ✅ **Organizations**: Count of all Organization objects
- ✅ **Assessments**: Count of completed UserAssessment objects

### **User Growth Chart (Last 12 Months):**
- ✅ Shows bars for each month (Jan, Feb, Mar, etc.)
- ✅ Height represents number of new users that month
- ✅ Calculated from User.created_at field
- ✅ Displays "Total new users: 0 months tracked" text

### **Assessment Types:**
- ✅ Shows breakdown by assessment name
- ✅ Progress bars showing percentage of each type
- ✅ Count next to each bar
- ✅ Empty state if no data

### **Severity Distribution:**
- ✅ Shows: Mild, Moderate, Moderately_Severe, Severe
- ✅ Color-coded bars (green=mild, yellow=moderate, red=severe)
- ✅ Percentage bars
- ✅ Count for each severity level

### **Organization Types:**
- ✅ Shows breakdown by organization_type field
- ✅ Purple progress bars
- ✅ Count for each type
- ✅ Empty state if no organizations

---

## 🔧 Code Changes

### File Modified:
**`core/admin_views.py`** - `admin_analytics_view()` function

### Key Changes:
```python
from collections import OrderedDict

# 1. Added total_organizations
context['total_organizations'] = Organization.objects.count()

# 2. Fixed variable name: assessment_breakdown → assessment_types
context['assessment_types'] = {...}

# 3. Added organization types
org_types = Organization.objects.values('organization_type').annotate(
    count=Count('id')
).order_by('-count')
context['org_types'] = {...}

# 4. Fixed monthly users
monthly_users = OrderedDict()
for i in range(11, -1, -1):
    month_start = timezone.now() - timedelta(days=30*(i+1))
    month_end = timezone.now() - timedelta(days=30*i)
    users_count = User.objects.filter(
        created_at__gte=month_start,  # Changed from date_joined
        created_at__lt=month_end
    ).count()
    month_key = month_start.strftime('%b')
    monthly_users[month_key] = users_count

context['monthly_users'] = monthly_users  # Changed from monthly_data
```

---

## 📊 Data Flow

### Template Expects → View Provides:
```
Template Variable          View Variable
─────────────────          ─────────────
total_users            →   User.objects.count()
total_organizations    →   Organization.objects.count() ✅ FIXED
total_assessments      →   UserAssessment.count()
monthly_users          →   OrderedDict of monthly counts ✅ FIXED
assessment_types       →   Dict of assessment breakdown ✅ FIXED
severity_distribution  →   Dict of severity levels
org_types              →   Dict of org types ✅ FIXED (NEW)
```

---

## 🧪 Testing

### Verify the Fix:
1. **Login as admin**
2. **Go to Admin Dashboard**
3. **Click "View Analytics"**
4. **Check each section:**

   ✅ **Top Stats:**
   - Should show actual counts for Users, Organizations, Assessments
   
   ✅ **User Growth Chart:**
   - Should show 12 bars (one per month)
   - Height based on new users that month
   - Even if 0, should show small bar
   
   ✅ **Assessment Types:**
   - If users completed assessments, shows breakdown
   - If no assessments, shows empty state
   
   ✅ **Severity Distribution:**
   - If assessments have results, shows severity breakdown
   - Color-coded bars
   
   ✅ **Organization Types:**
   - If organizations exist, shows type breakdown
   - If no organizations, shows empty state

---

## 🎯 Why It's Now Dynamic

### Before (Static/Broken):
- ❌ Hard-coded or missing data
- ❌ Wrong variable names
- ❌ Template couldn't find data
- ❌ Showed blanks and "No data available"

### After (Dynamic):
- ✅ **Real database queries** for all metrics
- ✅ **Correct variable names** matching template
- ✅ **Live data** - updates as system changes
- ✅ **Accurate counts** from actual models
- ✅ **Proper empty states** when no data exists

---

## 📈 Data Sources

### All Data is Queried Live:
```python
# Users
User.objects.count()  # Total users
User.objects.filter(created_at__gte=...).count()  # Monthly growth

# Organizations  
Organization.objects.count()  # Total organizations
Organization.objects.values('organization_type').annotate(count=Count('id'))  # By type

# Assessments
UserAssessment.objects.filter(is_completed=True).count()  # Total
UserAssessment.objects.values('assessment__name').annotate(count=Count('id'))  # By type

# Assessment Results
AssessmentResult.objects.values('severity_level').annotate(count=Count('id'))  # By severity

# Mood
MoodEntry.objects.count()  # Total mood entries
MoodEntry.objects.aggregate(avg_mood=Avg('mood'))  # Average mood
```

---

## ✅ Summary

### What Was Broken:
1. ❌ Organizations count missing
2. ❌ User growth chart empty
3. ❌ Assessment types blank
4. ❌ Organization types blank

### What Was Fixed:
1. ✅ Added `total_organizations` with correct count
2. ✅ Fixed `monthly_users` data structure and query
3. ✅ Renamed `assessment_breakdown` to `assessment_types`
4. ✅ Added `org_types` data (completely new)
5. ✅ Changed `date_joined` to `created_at` for User queries

### Result:
🎯 **All analytics data is now dynamic, accurate, and displays correctly!**

---

## 🔄 How It Updates

The analytics page shows **real-time data** from your database:
- ✅ Create a new user → User count increases
- ✅ User completes assessment → Assessment count increases, types update
- ✅ Create organization → Organization count increases, types update  
- ✅ Monthly growth updates automatically based on user created_at dates

**Everything is dynamic and based on actual database records!** 🌟

