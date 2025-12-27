# forms.py
from django import forms
from AdminApp.models import CRMFollowup
from django.utils import timezone

class FollowupNoteForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Enter your notes here...',
            'class': 'form-control'
        }),
        label='Note Content'
    )
    call_response = forms.ChoiceField(
        choices=CRMFollowup.CALL_RESPONSE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Call Response'
    )


class CRMFollowupUpdateForm(forms.ModelForm):
    # Customizing datetime inputs
    follow_up_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control datetime-picker'
            }
        ),
        required=False
    )
    
    next_followup_reminder = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control datetime-picker'
            }
        ),
        required=False
    )
    
    class_start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control datetime-picker'
            }
        ),
        required=False
    )
    
    # Customizing the notes field
    follow_up_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': 'Enter follow-up notes...'
        }),
        required=False
    )
    
    class Meta:
        model = CRMFollowup
        fields = [
            'name', 'mobile_number', 'student_interested_for', 'source',
            'status', 'priority', 'follow_up_by', 'call_response',
            'follow_up_date', 'next_followup_reminder', 'follow_up_notes',
            'class_start_date'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
            'student_interested_for': forms.Select(attrs={'class': 'form-select'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'follow_up_by': forms.Select(attrs={'class': 'form-select'}),
            'call_response': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set current datetime as default for date fields if they're empty
        current_datetime = timezone.now().strftime('%Y-%m-%dT%H:%M')
        
        if self.instance and not self.initial.get('follow_up_date') and not self.instance.follow_up_date:
            self.initial['follow_up_date'] = current_datetime
            
        if self.instance and not self.initial.get('next_followup_reminder') and not self.instance.next_followup_reminder:
            # Default next follow-up to 2 days from now
            from datetime import timedelta
            next_date = timezone.now() + timedelta(days=2)
            self.initial['next_followup_reminder'] = next_date.strftime('%Y-%m-%dT%H:%M')