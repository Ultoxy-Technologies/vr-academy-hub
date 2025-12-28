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

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

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
            'class_start_date','address','branch'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
            'student_interested_for': forms.Select(attrs={'class': 'form-select'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
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
    
    def clean_mobile_number(self):
        """Validate that mobile number is not duplicate for new records."""
        mobile_number = self.cleaned_data.get('mobile_number', '').strip()
        
        if not mobile_number:
            raise ValidationError("Mobile number is required.")
        
        # Check if this is a new record (instance doesn't have pk) or an update
        if not self.instance.pk:
            # This is a new record creation - check for duplicates
            if CRMFollowup.objects.filter(mobile_number=mobile_number).exists():
                # Find the existing record details
                existing_record = CRMFollowup.objects.filter(mobile_number=mobile_number).first()
                raise ValidationError(
                    f"Mobile number already exists. It belongs to: {existing_record.name} "
                    f"(Status: {existing_record.get_status_display()})"
                )
        # else:
        #     # This is an update - check for duplicates excluding the current record
        #     if CRMFollowup.objects.filter(mobile_number=mobile_number).exclude(pk=self.instance.pk).exists():
        #         # Find the existing record details (excluding current one)
        #         existing_record = CRMFollowup.objects.filter(mobile_number=mobile_number).exclude(pk=self.instance.pk).first()
        #         raise ValidationError(
        #             f"Mobile number already exists. It belongs to: {existing_record.name} "
        #             f"(Status: {existing_record.get_status_display()})"
        #         )
        
        # Additional validation for mobile number format
        if not mobile_number.isdigit():
            raise ValidationError("Mobile number should contain only digits.")
        
        if len(mobile_number) < 10 or len(mobile_number) > 15:
            raise ValidationError("Mobile number should be between 10 to 15 digits.")
        
        return mobile_number
    
    def clean(self):
        """Additional form-wide validation."""
        cleaned_data = super().clean()
        
        # Validate that follow-up date is not in the past (optional)
        follow_up_date = cleaned_data.get('follow_up_date')
 
        # Validate that next follow-up reminder is after follow-up date
        next_followup = cleaned_data.get('next_followup_reminder')
        if follow_up_date and next_followup and next_followup <= follow_up_date:
            self.add_error('next_followup_reminder', "Next follow-up should be after the current follow-up date.")
        
        # Validate that class start date is not before today (optional)
        class_start_date = cleaned_data.get('class_start_date')
        if class_start_date and class_start_date < timezone.now():
            self.add_error('class_start_date', "Class start date cannot be in the past.")
        
        return cleaned_data