from django import forms
from .models import Video, Comment, Category


class VideoUploadForm(forms.ModelForm):
    """Video upload form"""
    class Meta:
        model = Video
        fields = ['title', 'description', 'video_file', 'thumbnail', 'category', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter video title',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Tell viewers about your video',
                'rows': 4
            }),
            'video_file': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'video/*',
                'required': True
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            }),
            'category': forms.Select(attrs={
                'class': 'form-input'
            }),
            'status': forms.Select(attrs={
                'class': 'form-input'
            }),
        }
    
    def clean_video_file(self):
        video = self.cleaned_data.get('video_file')
        if video:
            # Check file size (3 GB limit)
            if video.size > 3 * 1024 * 1024 * 1024:
                raise forms.ValidationError('Video file size cannot exceed 3 GB.')
            
            # Check file extension
            import os
            ext = os.path.splitext(video.name)[1].lower()
            valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f'Invalid file format. Allowed formats: {", ".join(valid_extensions)}'
                )
        return video


class CommentForm(forms.ModelForm):
    """Comment form"""
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Add a comment...',
                'rows': 2
            }),
        }
