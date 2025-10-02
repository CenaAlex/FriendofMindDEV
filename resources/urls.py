from django.urls import path
from django.http import HttpResponse

app_name = 'resources'

def placeholder_view(request):
    return HttpResponse("Resources section coming soon!")

urlpatterns = [
    path('', placeholder_view, name='index'),
]



