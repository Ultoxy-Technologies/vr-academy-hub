from django import forms
from AdminApp.models import FreeCourse, FreeCourseProgress

class FreeCourseForm(forms.ModelForm):
    class Meta:
        model = FreeCourse
        fields = ['title', 'description', 'video', 'certificate_template']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'video': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'certificate_template': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
 

class FreeCourseProgressForm(forms.ModelForm):
    class Meta:
        model = FreeCourseProgress
        fields = ['student', 'course', 'watched_duration', 'completed']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'watched_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
