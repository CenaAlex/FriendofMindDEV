from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib import messages

class CheckUserActiveMiddleware:
    """
    Middleware to check if the logged-in user is still active.
    If a user's account is deactivated while they're logged in,
    they will be automatically logged out and redirected to the suspended page.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # List of paths that should be accessible even when suspended
        exempt_paths = [
            reverse('core:logout'),
            reverse('core:account_suspended'),
            reverse('core:landing'),
            reverse('core:modal_login'),
            '/admin/',  # Allow access to Django admin
            '/static/',  # Allow static files
            '/media/',   # Allow media files
        ]
        
        # Check if user is authenticated and not active
        if request.user.is_authenticated and not request.user.is_active:
            # Check if current path is not in exempt paths
            current_path = request.path
            is_exempt = any(current_path.startswith(path) for path in exempt_paths)
            
            if not is_exempt:
                # Log out the user
                logout(request)
                messages.warning(
                    request,
                    'Your account has been suspended. Please contact the support team for assistance.'
                )
                # Redirect to suspended page
                return redirect('core:account_suspended')
        
        response = self.get_response(request)
        return response

