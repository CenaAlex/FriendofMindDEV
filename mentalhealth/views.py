from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from .models import (
    MentalHealthResource, ResourceCategory, ProfessionalContact, 
    SelfHelpExercise, UserResourceInteraction
)

class ResourceListView(ListView):
    model = MentalHealthResource
    template_name = 'mentalhealth/resource_list.html'
    context_object_name = 'resources'
    paginate_by = 12
    
    def get_queryset(self):
        return MentalHealthResource.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ResourceCategory.objects.filter(is_active=True)
        return context

class ResourceByCategoryView(ListView):
    model = MentalHealthResource
    template_name = 'mentalhealth/resource_list.html'
    context_object_name = 'resources'
    paginate_by = 12
    
    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return MentalHealthResource.objects.filter(
            category_id=category_id, is_active=True
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ResourceCategory.objects.filter(is_active=True)
        context['current_category'] = get_object_or_404(
            ResourceCategory, id=self.kwargs['category_id']
        )
        return context

class ProfessionalListView(ListView):
    model = ProfessionalContact
    template_name = 'mentalhealth/professional_list.html'
    context_object_name = 'professionals'
    paginate_by = 12
    
    def get_queryset(self):
        return ProfessionalContact.objects.filter(is_active=True, is_verified=True)

class ProfessionalDetailView(DetailView):
    model = ProfessionalContact
    template_name = 'mentalhealth/professional_detail.html'
    pk_url_kwarg = 'contact_id'
    context_object_name = 'professional'

class SelfHelpExerciseListView(ListView):
    model = SelfHelpExercise
    template_name = 'mentalhealth/exercise_list.html'
    context_object_name = 'exercises'
    paginate_by = 12
    
    def get_queryset(self):
        return SelfHelpExercise.objects.filter(is_active=True)

class ExerciseDetailView(DetailView):
    model = SelfHelpExercise
    template_name = 'mentalhealth/exercise_detail.html'
    pk_url_kwarg = 'exercise_id'
    context_object_name = 'exercise'