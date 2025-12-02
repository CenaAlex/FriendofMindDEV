"""
Forms for Forum/Community System
"""
from django import forms
from .forum_models import ForumPost, ForumComment, ForumReport, ForumCommentReport


class ForumPostForm(forms.ModelForm):
    """Form for creating/editing forum posts"""
    class Meta:
        model = ForumPost
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800 text-white border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 resize-vertical',
                'rows': 4,
                'placeholder': "What's on your mind? Share your thoughts, experiences, or ask a question..."
            }),
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'imageInput',
                'accept': 'image/jpeg,image/jpg,image/png,image/gif'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = False
        self.fields['image'].required = False
        self.fields['content'].label = ''
        self.fields['image'].label = ''
    
    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        image = cleaned_data.get('image')
        
        # At least one of content or image must be provided
        if not content and not image:
            raise forms.ValidationError('Please provide either text content or an image.')
        
        return cleaned_data


class ForumCommentForm(forms.ModelForm):
    """Form for adding comments to posts"""
    class Meta:
        model = ForumComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 bg-gray-800 text-white border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 resize-vertical',
                'rows': 2,
                'placeholder': 'Add a comment...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].label = ''


class ForumReportForm(forms.ModelForm):
    """Form for reporting posts"""
    class Meta:
        model = ForumReport
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={
                'class': 'w-full px-4 py-2 bg-gray-800 text-white border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 bg-gray-800 text-white border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 resize-vertical',
                'rows': 3,
                'placeholder': 'Please provide additional details about why you are reporting this post...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].label = 'Reason for report'
        self.fields['description'].label = 'Additional details (optional)'
        self.fields['description'].required = False


class ForumCommentReportForm(forms.ModelForm):
    """Form for reporting comments"""
    class Meta:
        model = ForumCommentReport
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={
                'class': 'w-full px-4 py-2 bg-gray-800 text-white border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 bg-gray-800 text-white border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 resize-vertical',
                'rows': 3,
                'placeholder': 'Please provide additional details about why you are reporting this comment...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].label = 'Reason for report'
        self.fields['description'].label = 'Additional details (optional)'
        self.fields['description'].required = False


class AdminReportReviewForm(forms.ModelForm):
    """Form for admin to review reports"""
    class Meta:
        model = ForumReport
        fields = ['status', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'admin_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Internal notes about this report...'
            }),
        }


class AdminCommentReportReviewForm(forms.ModelForm):
    """Form for admin to review comment reports"""
    class Meta:
        model = ForumCommentReport
        fields = ['status', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'admin_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Internal notes about this report...'
            }),
        }

