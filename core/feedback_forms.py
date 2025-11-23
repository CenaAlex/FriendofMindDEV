"""
Forms for Feedback and Notification System
"""
from django import forms
from .feedback_models import Feedback, FeedbackResponse


class FeedbackForm(forms.ModelForm):
    """Form for users to submit feedback"""
    class Meta:
        model = Feedback
        fields = ['feedback_type', 'subject', 'message']
        widgets = {
            'feedback_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 bg-white bg-opacity-10 border border-gray-300 rounded-lg text-white focus:ring-2 focus:ring-blue-500'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 bg-white bg-opacity-10 border border-gray-300 rounded-lg text-white focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Brief description of your feedback'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 bg-white bg-opacity-10 border border-gray-300 rounded-lg text-white focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Please provide details...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['feedback_type'].label = 'Type'
        self.fields['subject'].label = 'Subject'
        self.fields['message'].label = 'Message'


class FeedbackResponseForm(forms.ModelForm):
    """Form for admins to respond to feedback"""
    class Meta:
        model = FeedbackResponse
        fields = ['message', 'is_internal_note']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Type your response here...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'is_internal_note':
                self.fields[field].widget.attrs.update({'class': 'form-control'})


class FeedbackUpdateForm(forms.ModelForm):
    """Form for admins to update feedback status and priority"""
    class Meta:
        model = Feedback
        fields = ['status', 'priority']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

