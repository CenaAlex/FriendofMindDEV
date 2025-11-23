from django import forms
from .models import Assessment, Question, AnswerChoice

class AssessmentForm(forms.ModelForm):
    """Form for creating/editing assessments"""
    class Meta:
        model = Assessment
        fields = ['name', 'title', 'description', 'instructions', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'name': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'is_active':
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class QuestionForm(forms.ModelForm):
    """Form for creating/editing questions"""
    class Meta:
        model = Question
        fields = ['text', 'order']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class AnswerChoiceForm(forms.ModelForm):
    """Form for creating/editing answer choices"""
    class Meta:
        model = AnswerChoice
        fields = ['text', 'value', 'order']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

