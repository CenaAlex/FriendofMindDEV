from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class CheckUserActiveMiddleware:
    """
    Middleware to handle deactivated and deleted user accounts.
    
    - If a logged-in user's account is deactivated (is_active=False):
      Logs them out and redirects to login page with a message.
      
    - If a logged-in user's account is deleted:
      Redirects to landing page.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip check for account-suspended page to avoid redirect loop
        if request.path == '/account-suspended/':
            return self.get_response(request)
        
        # Only check authenticated users
        if request.user.is_authenticated:
            try:
                # Try to get the user fresh from the database
                user = User.objects.get(pk=request.user.pk)
                
                # Check if the account is deactivated
                if not user.is_active:
                    # Store username in session before logout for reactivation request
                    username = user.username
                    email = user.email
                    logout(request)
                    request.session['deactivated_username'] = username
                    request.session['deactivated_email'] = email
                    return redirect('core:account_suspended')
                    
            except User.DoesNotExist:
                # User was deleted from the database
                logout(request)
                messages.error(
                    request, 
                    'Your account no longer exists. Please sign up to create a new account.'
                )
                return redirect('core:landing')
        
        response = self.get_response(request)
        return response
