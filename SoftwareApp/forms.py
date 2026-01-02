# forms.py
from django import forms
from AdminApp.models import CRMFollowup, Enrollment, Batch, Payment,Basic_to_Advance_Cource, Advance_to_Pro_Cource
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


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
    








 
class EnrollmentForm(forms.ModelForm):
    """Form for creating and updating enrollment records"""
    
    # Additional fields for student selection
    student_mobile = forms.CharField(
        max_length=15,
        required=True,
        label="Student Mobile Number",
        help_text="Enter existing student's mobile number or add new student"
    )
    
    student_name = forms.CharField(
        max_length=150,
        required=True,
        label="Student Name",
        help_text="Enter student's full name"
    )
    
    # Custom field for batch selection with enhanced display
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.filter(is_active=True),
        required=True,
        label="Select Batch",
        help_text="Choose an active batch for enrollment",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Enrollment
        fields = [
            'student_mobile', 'student_name', 'batch',
            'total_fees', 'discount', 'status', 'payment_status',
            'class_start_date', 'class_end_date', 'payment_schedule'
        ]
        widgets = {
            'total_fees': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 15000.00',
                'step': '0.01'
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1000.00',
                'step': '0.01'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'class_start_date': forms.DateInput(attrs={
                'class': 'form-control datetime-picker',
                'type': 'date'
            }),
            'class_end_date': forms.DateInput(attrs={
                'class': 'form-control datetime-picker',
                'type': 'date'
            }),
            'payment_schedule': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g., 5000 on 10th Dec, 5000 on 10th Jan, 5000 on 10th Feb'
            }),
        }
        help_texts = {
            'total_fees': 'Total course fees for this enrollment',
            'discount': 'Discount amount (if any)',
            'payment_schedule': 'Optional: Describe the payment schedule',
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.student_instance = kwargs.pop('student_instance', None)
        self.is_update = kwargs.pop('is_update', False)
        
        super().__init__(*args, **kwargs)
        
        # If updating, set initial values
        if self.instance and self.instance.pk:
            self.fields['student_mobile'].initial = self.instance.student.mobile_number
            self.fields['student_mobile'].disabled = True  # Can't change mobile on update
            self.fields['student_name'].initial = self.instance.student.name
            self.fields['batch'].initial = self.instance.batch
            
            # Set fee-related fields
            self.fields['total_fees'].initial = self.instance.total_fees
            self.fields['discount'].initial = self.instance.discount
        
        # Customize queryset for batch field
        self.fields['batch'].queryset = Batch.objects.filter(is_active=True)
        
        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['batch', 'status', 'payment_status']:
                if not hasattr(field.widget, 'attrs'):
                    field.widget.attrs = {}
                field.widget.attrs['class'] = 'form-control'
    
    def clean_student_mobile(self):
        """Validate and find/create student based on mobile number"""
        mobile_number = self.cleaned_data.get('student_mobile')
        
        if not mobile_number:
            raise ValidationError("Mobile number is required")
        
        # Validate mobile number format (basic validation)
        if len(mobile_number) < 10:
            raise ValidationError("Mobile number must be at least 10 digits")
        
        # Check if mobile number contains only digits
        if not mobile_number.isdigit():
            raise ValidationError("Mobile number should contain only digits")
        
        return mobile_number
    
    def clean_student_name(self):
        """Validate student name"""
        name = self.cleaned_data.get('student_name')
        if not name:
            raise ValidationError("Student name is required")
        return name.strip()
    
    def clean_total_fees(self):
        """Validate total fees"""
        total_fees = self.cleaned_data.get('total_fees')
        if total_fees is not None and total_fees < 0:
            raise ValidationError("Total fees cannot be negative")
        return total_fees or Decimal('0.00')
    
    def clean_discount(self):
        """Validate discount"""
        discount = self.cleaned_data.get('discount')
        total_fees = self.cleaned_data.get('total_fees')
        
        if discount is not None:
            if discount < 0:
                raise ValidationError("Discount cannot be negative")
            if total_fees and discount > total_fees:
                raise ValidationError("Discount cannot exceed total fees")
        
        return discount or Decimal('0.00')
    
    def clean_class_start_date(self):
        """Validate class start date"""
        start_date = self.cleaned_data.get('class_start_date')
        if start_date and start_date < timezone.now().date():
            raise ValidationError("Class start date cannot be in the past")
        return start_date
    
    def clean_class_end_date(self):
        """Validate class end date"""
        start_date = self.cleaned_data.get('class_start_date')
        end_date = self.cleaned_data.get('class_end_date')
        
        if start_date and end_date and end_date < start_date:
            raise ValidationError("Class end date cannot be before start date")
        
        return end_date
    
    def clean(self):
        """Main validation - check for duplicate enrollment"""
        cleaned_data = super().clean()
        
        if self.errors:
            return cleaned_data
        
        mobile_number = cleaned_data.get('student_mobile')
        batch = cleaned_data.get('batch')
        student_name = cleaned_data.get('student_name')
        
        if not mobile_number or not batch:
            return cleaned_data
        
        # Import CustomUser model
        from django.contrib.auth import get_user_model
        CustomUser = get_user_model()
        
        # Check for duplicate enrollment (same student + same batch)
        try:
            # Find student by mobile number
            student = CustomUser.objects.get(mobile_number=mobile_number)
            
            # Check if enrollment already exists for this student and batch
            existing_enrollment = Enrollment.objects.filter(
                student=student,
                batch=batch
            )
            
            # If updating, exclude current instance
            if self.instance and self.instance.pk:
                existing_enrollment = existing_enrollment.exclude(pk=self.instance.pk)
            
            if existing_enrollment.exists():
                raise ValidationError(
                    f"Student {student.name} is already enrolled in batch {batch.batch_code}. "
                    f"Please select a different batch or update the existing enrollment."
                )
            
        except CustomUser.DoesNotExist:
            # Student doesn't exist yet, will be created in save()
            pass
        except CustomUser.MultipleObjectsReturned:
            raise ValidationError(
                f"Multiple students found with mobile number {mobile_number}. "
                f"Please contact administrator."
            )
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save enrollment with student creation/update"""
        try:
            # Get or create student
            from django.contrib.auth import get_user_model
            CustomUser = get_user_model()
            
            mobile_number = self.cleaned_data['student_mobile']
            student_name = self.cleaned_data['student_name']
            
            # Try to find existing student
            try:
                student = CustomUser.objects.get(mobile_number=mobile_number)
                # Update student name if changed
                if student.name != student_name:
                    student.name = student_name
                    student.save()
            except CustomUser.DoesNotExist:
                # Create new student
                student = CustomUser.objects.create(
                    mobile_number=mobile_number,
                    name=student_name,
                    role='is_student',  # Default role for students
                    is_active=True,
                    email=f"{mobile_number}@example.com",  # Temporary email
                    username=mobile_number  # Use mobile as username
                )
            
            # Set student and batch on enrollment
            self.instance.student = student
            self.instance.batch = self.cleaned_data['batch']
            
            # Auto-set course title from batch
            batch = self.cleaned_data['batch']
            if batch.basic_to_advance_cource:
                self.instance.course_title = batch.basic_to_advance_cource.title
            elif batch.advance_to_pro_cource:
                self.instance.course_title = batch.advance_to_pro_cource.title
            
            # Calculate net fees
            total_fees = self.cleaned_data.get('total_fees') or Decimal('0.00')
            discount = self.cleaned_data.get('discount') or Decimal('0.00')
            self.instance.net_fees = total_fees - discount
            
            # Set enrollment date if new record
            if not self.instance.pk:
                self.instance.enrollment_date = timezone.now().date()
            
            # Save the enrollment
            if commit:
                self.instance.save()
            
            return self.instance
            
        except Exception as e:
            raise ValidationError(f"Error saving enrollment: {str(e)}")
        





# forms.py - Alternative using actual model fields
class BatchForm(forms.ModelForm):
    """Form for creating and updating batch records"""
    
    class Meta:
        model = Batch
        fields = [
            'batch_code', 'batch_title', 'batch_status',
            'basic_to_advance_cource', 'advance_to_pro_cource',
            'start_date', 'end_date',
            'max_students', 'description',
            'is_active'
        ]
        widgets = {
            'batch_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., BATCH-2024-001'
            }),
            'batch_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Python Fundamentals Batch'
            }),
            'batch_status': forms.Select(attrs={'class': 'form-select'}),
            'basic_to_advance_cource': forms.Select(attrs={
                'class': 'form-select course-select',
                'data-course-type': 'basic'
            }),
            'advance_to_pro_cource': forms.Select(attrs={
                'class': 'form-select course-select',
                'data-course-type': 'advance'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control datetime-picker',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control datetime-picker',
                'type': 'date'
            }),
            'max_students': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'step': '1'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter batch description, schedule, requirements...'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        help_texts = {
            'batch_code': 'Unique batch code (e.g., BATCH-2024-001)',
            'batch_title': 'Display name for the batch',
            'basic_to_advance_cource': 'Select Basic to Advance course',
            'advance_to_pro_cource': 'Select Advance to Pro course',
            'max_students': 'Maximum number of students allowed in this batch',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set queryset for course fields
        self.fields['basic_to_advance_cource'].queryset = Basic_to_Advance_Cource.objects.filter(is_active=True)
        self.fields['advance_to_pro_cource'].queryset = Advance_to_Pro_Cource.objects.filter(is_active=True)
        
        # Make both fields not required in form (we'll validate in clean)
        self.fields['basic_to_advance_cource'].required = False
        self.fields['advance_to_pro_cource'].required = False
        
        # Add CSS classes
        for field_name, field in self.fields.items():
            if field_name not in ['batch_status', 'is_active']:
                if not hasattr(field.widget, 'attrs'):
                    field.widget.attrs = {}
                field.widget.attrs['class'] = 'form-control'
    
    def clean(self):
        """Ensure only one course is selected"""
        cleaned_data = super().clean()
        
        basic_course = cleaned_data.get('basic_to_advance_cource')
        advance_course = cleaned_data.get('advance_to_pro_cource')
        
        # Check if at least one course is selected
        if not basic_course and not advance_course:
            raise ValidationError("Please select at least one course (Basic to Advance or Advance to Pro)")
        
        # Check if both courses are selected
        if basic_course and advance_course:
            raise ValidationError("Cannot select both Basic to Advance and Advance to Pro courses. Please choose only one.")
        
        return cleaned_data