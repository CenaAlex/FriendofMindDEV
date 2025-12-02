from django.urls import path, include
from django.shortcuts import redirect

app_name = 'resources'

def redirect_to_mentalhealth(request):
    """Redirect to mentalhealth resources"""
    return redirect('mentalhealth:resource_list')

# Import the enhanced views from mentalhealth app
from mentalhealth import resource_enhanced_views as enhanced

urlpatterns = [
    # Redirect root to mentalhealth resources
    path('', redirect_to_mentalhealth, name='index'),
    
    # Bookmarking (for AJAX calls from frontend)
    path('bookmark/<int:resource_id>/', enhanced.bookmark_resource, name='bookmark_resource'),
    path('my-bookmarks/', enhanced.my_bookmarks, name='my_bookmarks'),
    
    # Reporting
    path('report/<int:resource_id>/', enhanced.report_resource, name='report_resource'),
    
    # All other resource URLs handled by mentalhealth app
    path('resource/<int:resource_id>/', enhanced.ResourceDetailView.as_view(), name='resource_detail'),
]



