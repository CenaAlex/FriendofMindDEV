from django.urls import path
from django.http import HttpResponse

app_name = 'assessments'

def placeholder_view(request):
    return HttpResponse("Assessments section coming soon!")

urlpatterns = [
    path('', placeholder_view, name='index'),
]



