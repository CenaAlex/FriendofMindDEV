# Data Sync Issue - New Users Showing False Data

## Problem Reported

When creating a new user through the admin panel and logging in as that user, the dashboard showed **fake data** instead of showing zeros/empty state:

- **Days Active:** Showed 7 (should be 0)
- **Assessments Completed:** Showed 3 (should be 0)  
- **Resources Accessed:** Showed 4 (should be 0)
- **Wellness Score:** Calculated based on fake assessment count

## Root Cause

The issue was **NOT** with data filtering or user sync. The backend was correctly filtering data by user. The problem was in the **dashboard template** using hardcoded default values and fake numbers!

### The Bug in `templates/core/dashboard.html`

#### Line 13 - Days Active:
```django
<h3 class="text-3xl font-bold">{{ recent_moods.count|default:7 }}</h3>
```
❌ **Problem:** Used `default:7` - if user has no moods, show 7!  
✅ **Fixed:** Changed to `default:0`

#### Line 19 - Assessments Completed:
```django
<h3 class="text-3xl font-bold">{{ assessments_taken|default:3 }}</h3>
```
❌ **Problem:** Used `default:3` - if user has no assessments, show 3!  
✅ **Fixed:** Changed to `default:0`

#### Line 25 - Resources Accessed:
```django
<h3 class="text-3xl font-bold">4</h3>
```
❌ **Problem:** Hardcoded `4` - always shows 4 regardless of user!  
✅ **Fixed:** Changed to `{{ resources_accessed|default:0 }}` with backend support

---

## The Fix

### 1. Fixed Dashboard Template (`templates/core/dashboard.html`)

**Before:**
```django
<div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
    <a href="{% url 'core:mood_history' %}">
        <h3 class="text-3xl font-bold">{{ recent_moods.count|default:7 }}</h3>
        <p class="text-lg">Days Active</p>
    </a>
    <a href="{% url 'screening:assessment_history' %}">
        <h3 class="text-3xl font-bold">{{ assessments_taken|default:3 }}</h3>
        <p class="text-lg">Assessments Completed</p>
    </a>
    <a href="{% url 'mentalhealth:resource_list' %}">
        <h3 class="text-3xl font-bold">4</h3>  <!-- Hardcoded! -->
        <p class="text-lg">Resources Accessed</p>
    </a>
</div>
```

**After:**
```django
<div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
    <a href="{% url 'core:mood_history' %}">
        <h3 class="text-3xl font-bold">{{ recent_moods.count|default:0 }}</h3>
        <p class="text-lg">Days Active</p>
    </a>
    <a href="{% url 'screening:assessment_history' %}">
        <h3 class="text-3xl font-bold">{{ assessments_taken|default:0 }}</h3>
        <p class="text-lg">Assessments Completed</p>
    </a>
    <a href="{% url 'mentalhealth:resource_list' %}">
        <h3 class="text-3xl font-bold">{{ resources_accessed|default:0 }}</h3>
        <p class="text-lg">Resources Accessed</p>
    </a>
</div>
```

### 2. Added Backend Support for Resources Accessed (`core/views.py`)

Added to `DashboardView.get_context_data()`:

```python
# Resources accessed (currently not tracked, set to 0)
# TODO: Implement resource tracking system
context['resources_accessed'] = 0
```

**Note:** Resources tracking is not implemented yet. When it is, update this to actually count resources accessed by the user.

---

## Backend Data Filtering - Already Correct! ✅

The backend was **already correctly** filtering data by user. No changes needed:

```python
class DashboardView(LoginRequiredMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user  # ✅ Correct: Gets current user
        
        # ✅ All queries filter by user
        context['recent_moods'] = MoodEntry.objects.filter(user=user)[:7]
        completed_assessments = UserAssessment.objects.filter(user=user, is_completed=True)
        context['assessments_taken'] = completed_assessments.count()
        latest_results = AssessmentResult.objects.filter(
            user_assessment__user=user,
            user_assessment__is_completed=True
        ).order_by('-created_at')[:3]
        # ... etc
```

All data is properly filtered by the logged-in user. The issue was purely cosmetic in the template!

---

## What New Users See Now

### Before Fix (❌ Wrong):
```
Dashboard for new_user
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Days Active │ Assessments │  Resources  │  Wellness   │
│      7      │      3      │      4      │     70%     │
└─────────────┴─────────────┴─────────────┴─────────────┘
```
**Problem:** Looks like user has data when they don't!

### After Fix (✅ Correct):
```
Dashboard for new_user
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Days Active │ Assessments │  Resources  │  Wellness   │
│      0      │      0      │      0      │      0%     │
└─────────────┴─────────────┴─────────────┴─────────────┘
```
**Perfect:** Accurately reflects that user has no data yet!

---

## Testing

### Test Case 1: Brand New User
```
1. Admin creates new user via System Admin → Users → Create User
2. Log in as that new user
3. ✅ Dashboard shows:
   - Days Active: 0
   - Assessments Completed: 0
   - Resources Accessed: 0
   - Wellness Score: 0%
   - No mood data
   - No assessment results
```

### Test Case 2: User Adds Data
```
1. User logs their first mood entry
2. Refresh dashboard
3. ✅ Days Active: 1 (increments correctly)

4. User completes an assessment
5. Refresh dashboard
6. ✅ Assessments Completed: 1
7. ✅ Wellness Score: 70% (calculated correctly)
```

### Test Case 3: Different Users Have Different Data
```
1. User A has 3 moods, 2 assessments
2. User B has 0 moods, 0 assessments (new)
3. ✅ User A sees: Days Active: 3, Assessments: 2
4. ✅ User B sees: Days Active: 0, Assessments: 0
5. ✅ No data leaks between users
```

---

## Files Modified

### ✅ `templates/core/dashboard.html`
- Changed `default:7` to `default:0` for Days Active
- Changed `default:3` to `default:0` for Assessments Completed
- Changed hardcoded `4` to `{{ resources_accessed|default:0 }}`

### ✅ `core/views.py`
- Added `context['resources_accessed'] = 0` to DashboardView
- Added TODO comment for future resource tracking implementation

---

## Why This Happened

This appears to be **demo/mock data** that was left in from development:

1. **Default values** were probably used during development to show how the dashboard would look with data
2. **Hardcoded numbers** were placeholders for features not yet implemented (resources tracking)
3. These were **never cleaned up** before deployment

---

## Prevention

To prevent this in the future:

### ❌ DON'T:
```django
<!-- Bad: Shows fake data for new users -->
<h3>{{ user_data|default:99 }}</h3>
```

### ✅ DO:
```django
<!-- Good: Shows 0 for new users -->
<h3>{{ user_data|default:0 }}</h3>
```

### For Hardcoded Values:
```django
<!-- Bad: Always shows same number -->
<h3>42</h3>

<!-- Good: Shows actual data from backend -->
<h3>{{ actual_count|default:0 }}</h3>
```

---

## Related Issues

### Resources Accessed
Currently **not implemented** in the backend. Options for future implementation:

1. **Track resource views:** Log when users access mental health resources
2. **Track resource downloads:** Count PDF/document downloads
3. **Track resource bookmarks:** Count saved/favorited resources
4. **Track professional contacts:** Count when users contact professionals

**For now:** Shows 0 for all users (correct behavior for unimplemented feature)

---

## Summary

✅ **Issue:** New users showed fake data (7 days, 3 assessments, 4 resources)  
✅ **Cause:** Template using wrong default values and hardcoded numbers  
✅ **Fix:** Changed defaults to 0 and added backend variable  
✅ **Result:** New users now correctly show zero data  
✅ **Data Security:** No actual data leaks - was purely cosmetic  
✅ **Testing:** All user data is properly isolated and filtered  

**The system is now showing accurate, user-specific data!** 🎉

