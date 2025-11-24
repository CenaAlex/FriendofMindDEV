# Assessment Debugging Guide

## 🔍 Debugging Added

I've added console logging to help us find exactly where the issue is.

---

## 🧪 How to Debug:

### Step 1: Open Browser Console
1. Press **F12** (or right-click → Inspect)
2. Click the **"Console"** tab
3. Keep this open

### Step 2: Refresh the Assessment Page
1. Press **Ctrl+F5** to hard refresh
2. **Look for in console:**
   ```
   Assessment page loaded
   DOMContentLoaded fired
   ```

### Step 3: Select an Answer
1. Click any answer choice
2. **Look for in console:**
   ```
   Answer selected: [some number]
   ```

### Step 4: Click "Next" Button
1. Click the "Next" button
2. **Look for in console:**
   ```
   Validating form...
   Form valid, submitting...
   Form submitting...
   ```

### Step 5: Check Terminal Output
Look at your terminal (where `python manage.py runserver` is running) for:
```
DEBUG: POST received - Action: next, Answer: [some number]
DEBUG: Answer choice found: [answer text]
DEBUG: Created new answer
DEBUG: Going to next question: 2
```

---

## 📊 What to Look For:

### If Console Shows:
- ✅ **All messages appear** → Form is working, check terminal
- ❌ **"Assessment page loaded" missing** → JavaScript not loading
- ❌ **No "Answer selected"** → Radio buttons not working
- ❌ **"Please select an answer" alert** → Form validation working
- ❌ **Nothing after clicking Next** → Form not submitting

### If Terminal Shows:
- ✅ **"DEBUG: POST received"** → View is receiving form data
- ✅ **"DEBUG: Going to next question"** → Should redirect
- ❌ **No DEBUG messages** → Form not reaching server
- ❌ **Error messages** → Tell me what they say

---

## 🚨 Common Issues:

### Issue 1: Form Not Submitting
**Console shows:** Nothing after "Form submitting..."
**Fix:** Browser might be blocking - try different browser

### Issue 2: POST Not Reaching Server
**Console shows:** Form messages, but no terminal DEBUG
**Fix:** Check if server is running, refresh server

### Issue 3: JavaScript Errors
**Console shows:** Red error messages
**Fix:** Copy the error and send it to me

### Issue 4: CSRF Token Error
**Console/Terminal shows:** "CSRF verification failed"
**Fix:** Clear browser cookies and try again

---

## 📋 Send Me This Info:

After testing, tell me:

1. **Browser Console Output:**
   ```
   [paste what you see in console]
   ```

2. **Terminal Output:**
   ```
   [paste DEBUG messages from terminal]
   ```

3. **What Happens:**
   - Does the page refresh?
   - Does it stay on same question?
   - Does it show error message?
   - Any red errors in console?

---

## 🎯 Quick Test Script:

Copy this into your browser console and press Enter:
```javascript
// Check if form exists
console.log('Form:', document.getElementById('questionForm'));

// Check if radio buttons exist
console.log('Radio buttons:', document.querySelectorAll('input[type="radio"]').length);

// Check if validateForm function exists
console.log('validateForm function:', typeof validateForm);

// Try to submit form programmatically
console.log('Submitting form...');
document.getElementById('questionForm').submit();
```

This will tell us if everything is loaded correctly!

---

## 🔧 Current Debugging Features:

### In Template:
- Console log when page loads
- Console log when DOMContentLoaded fires
- Console log when answer selected
- Console log when validating form
- Console log when form submits
- Console log on button clicks

### In View:
- Print POST data received
- Print action type (next/back/submit)
- Print answer ID
- Print answer choice found
- Print if creating new/updating existing answer
- Print navigation decisions

---

With this debugging, we'll find exactly where the problem is! 🕵️‍♂️

