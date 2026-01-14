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
            'class_start_date', 'class_end_date', 'payment_schedule','branch'
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
    
    # def clean_class_start_date(self):
    #     """Validate class start date"""
    #     start_date = self.cleaned_data.get('class_start_date')
    #     if start_date and start_date < timezone.now().date():
    #         raise ValidationError("Class start date cannot be in the past")
    #     return start_date
    
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
    
 

class PaymentForm(forms.ModelForm):
    """Form for recording payments"""
    
 
    # Field for selecting installment
    installment_number = forms.IntegerField(
        required=False,
        label="Installment Number",
        help_text="e.g., 1 for first installment"
    )
    
    class Meta:
        model = Payment
        fields = [
            'payment_type', 'amount', 'payment_date', 'payment_mode',
            'installment_number', 'due_date', 'reference_number', 'remarks'
        ]
        widgets = {
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 5000.00',
                'step': '0.01'
            }),
            'payment_date': forms.DateInput(attrs={
                'class': 'form-control datetime-picker',
                'type': 'date'
            }),
            'payment_mode': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control datetime-picker',
                'type': 'date'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., TXN123456'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about this payment'
            }),
        }
        help_texts = {
            'payment_type': 'Type of payment (installment, admission, etc.)',
            'amount': 'Amount received',
            'payment_date': 'Date when payment was received',
            'payment_mode': 'Mode of payment',
            'due_date': 'Due date for installment (if applicable)',
            'reference_number': 'Transaction/Cheque/Reference number',
        }
    
    def __init__(self, *args, **kwargs):
        self.enrollment = kwargs.pop('enrollment', None)
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Set payment date to today by default
        if not self.instance.pk:
            self.fields['payment_date'].initial = timezone.now().date()
        
        # If installment payment, suggest next installment number
        if self.enrollment and not self.instance.pk:
            last_installment = self.enrollment.payments.filter(
                installment_number__isnull=False
            ).order_by('-installment_number').first()
            
            if last_installment and last_installment.installment_number:
                next_installment = last_installment.installment_number + 1
                self.fields['installment_number'].initial = next_installment
        
        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['payment_type', 'payment_mode']:
                if not hasattr(field.widget, 'attrs'):
                    field.widget.attrs = {}
                field.widget.attrs['class'] = 'form-control'
    
 
    
    def clean_amount(self):
        """Validate payment amount"""
        amount = self.cleaned_data.get('amount')
        
        if not amount:
            raise ValidationError("Payment amount is required")
        
        if amount <= 0:
            raise ValidationError("Payment amount must be greater than 0")
        
        # Check if payment exceeds remaining balance
        if self.enrollment:
            remaining_balance = self.enrollment.balance
            if amount > remaining_balance:
                raise ValidationError(
                    f"Payment amount (₹{amount}) exceeds remaining balance (₹{remaining_balance})"
                )
        
        return amount
    
    def clean_payment_date(self):
        """Validate payment date"""
        payment_date = self.cleaned_data.get('payment_date')
        if payment_date and payment_date > timezone.now().date():
            raise ValidationError("Payment date cannot be in the future")
        return payment_date
    
    def clean_due_date(self):
        """Validate due date"""
        due_date = self.cleaned_data.get('due_date')
        payment_date = self.cleaned_data.get('payment_date')
        
        if due_date and payment_date and due_date < payment_date:
            raise ValidationError("Due date cannot be before payment date")
        
        return due_date
    
    def clean_installment_number(self):
        """Validate installment number"""
        installment_number = self.cleaned_data.get('installment_number')
        payment_type = self.cleaned_data.get('payment_type')
        
        if payment_type == 'installment' and not installment_number:
            raise ValidationError("Installment number is required for installment payments")
        
        if installment_number is not None and installment_number <= 0:
            raise ValidationError("Installment number must be positive")
        
        # Check for duplicate installment number for this enrollment
        if installment_number and self.enrollment:
            existing_payment = self.enrollment.payments.filter(
                installment_number=installment_number
            )
            
            # If updating, exclude current instance
            if self.instance and self.instance.pk:
                existing_payment = existing_payment.exclude(pk=self.instance.pk)
            
            if existing_payment.exists():
                raise ValidationError(
                    f"Installment #{installment_number} already exists for this enrollment"
                )
        
        return installment_number
    
    def clean(self):
        """Main validation"""
        cleaned_data = super().clean()
        
        # Validate payment mode for cheque payments
        payment_mode = cleaned_data.get('payment_mode')
        reference_number = cleaned_data.get('reference_number')
        
        if payment_mode == 'cheque' and not reference_number:
            raise ValidationError("Cheque number is required for cheque payments")
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save payment with enrollment link"""
        payment = super().save(commit=False)
        
        # Set enrollment
        if self.enrollment:
            payment.enrollment = self.enrollment
        
        # Set received by user
        if self.request and self.request.user:
            payment.received_by = self.request.user
        
        # Set installment number if provided
        installment_number = self.cleaned_data.get('installment_number')
        if installment_number:
            payment.installment_number = installment_number
        
        if commit:
            payment.save()
            
            # Update enrollment payment status
            if self.enrollment:
                self.enrollment.update_payment_status()
                self.enrollment.save()
        
        return payment
    



from AdminApp.models import Branch, CRM_Student_Interested_for_options

    # forms.py (add to existing forms)


class BranchForm(forms.ModelForm):
    """Form for creating and updating Branch records"""
    
    class Meta:
        model = Branch
        fields = ['branch_name']
        widgets = {
            'branch_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Main Branch, Mumbai Branch, etc.'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            if not hasattr(field.widget, 'attrs'):
                field.widget.attrs = {}
            field.widget.attrs['class'] = 'form-control'
    
    def clean_branch_name(self):
        """Validate branch name"""
        branch_name = self.cleaned_data.get('branch_name')
        if not branch_name:
            raise ValidationError("Branch name is required")
        
        # Check for duplicates (case-insensitive)
        branch_name_clean = branch_name.strip()
        
        # If updating, exclude current instance
        if self.instance and self.instance.pk:
            existing = Branch.objects.filter(
                branch_name__iexact=branch_name_clean
            ).exclude(pk=self.instance.pk)
        else:
            existing = Branch.objects.filter(
                branch_name__iexact=branch_name_clean
            )
        
        if existing.exists():
            raise ValidationError(f"A branch with name '{branch_name}' already exists")
        
        return branch_name_clean
    

# forms.py (add to existing forms)

class StudentInterestForm(forms.ModelForm):
    """Form for creating and updating student interest options"""
    
    class Meta:
        model = CRM_Student_Interested_for_options
        fields = ['interest_option']
        widgets = {
            'interest_option': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Python Programming, Web Development, Data Science, etc.'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            if not hasattr(field.widget, 'attrs'):
                field.widget.attrs = {}
            field.widget.attrs['class'] = 'form-control'
    
    def clean_interest_option(self):
        """Validate interest option"""
        interest_option = self.cleaned_data.get('interest_option')
        if not interest_option:
            raise ValidationError("Interest option is required")
        
        # Check for duplicates (case-insensitive)
        interest_option_clean = interest_option.strip()
        
        # If updating, exclude current instance
        if self.instance and self.instance.pk:
            existing = CRM_Student_Interested_for_options.objects.filter(
                interest_option__iexact=interest_option_clean
            ).exclude(pk=self.instance.pk)
        else:
            existing = CRM_Student_Interested_for_options.objects.filter(
                interest_option__iexact=interest_option_clean
            )
        
        if existing.exists():
            raise ValidationError(f"Interest option '{interest_option}' already exists")
        
        return interest_option_clean



# forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from AdminApp.models import Event, EventRegistration
import json

class EventForm(forms.ModelForm):
    """Form for creating and updating events"""
    
    # Custom field for tags with better UX
    tags_input = forms.CharField(
        required=False,
        label="Tags",
        help_text="Enter tags separated by commas (e.g., Technology, Education, Workshop)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Technology, Education, Workshop'
        })
    )
    
    class Meta:
        model = Event
        fields = [
            'thumbnail', 'title', 'subtitle', 'description',
            'category', 'tags_input', 'event_date', 'event_start_time',
            'event_end_time', 'timezone', 'meeting_link', 'meeting_id',
            'meeting_password', 'is_free', 'registration_strickthrough_fee',
            'registration_offer_fee', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter event title'
            }),
            'subtitle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional subtitle'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Detailed description of the event...'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Webinar, Workshop, Conference'
            }),
            'event_date': forms.DateInput(attrs={
                'class': 'form-control datetime-picker',
                'type': 'date'
            }),
            'event_start_time': forms.TimeInput(attrs={
                'class': 'form-control datetime-picker',
                'type': 'time'
            }),
            'event_end_time': forms.TimeInput(attrs={
                'class': 'form-control datetime-picker',
                'type': 'time'
            }),
            'timezone': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('IST', 'Indian Standard Time (IST)'),
                ('UTC', 'Coordinated Universal Time (UTC)'),
                ('EST', 'Eastern Standard Time (EST)'),
                ('PST', 'Pacific Standard Time (PST)'),
                ('CET', 'Central European Time (CET)'),
            ]),
            'meeting_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://zoom.us/j/1234567890'
            }),
            'meeting_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 123 456 7890'
            }),
            'meeting_password': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter meeting password'
            }),
            'registration_strickthrough_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1000.00',
                'step': '0.01'
            }),
            'registration_offer_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 799.00',
                'step': '0.01'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_free': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        help_texts = {
            'thumbnail': 'Recommended size: 800x600 pixels',
            'registration_strickthrough_fee': 'Original price (for strikethrough display)',
            'registration_offer_fee': 'Discounted or current price',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If updating, convert tags JSON to comma-separated string
        if self.instance and self.instance.pk and self.instance.tags:
            tags_list = self.instance.tags
            if isinstance(tags_list, list):
                self.fields['tags_input'].initial = ', '.join(tags_list)
        
        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['is_free', 'status', 'timezone']:
                if not hasattr(field.widget, 'attrs'):
                    field.widget.attrs = {}
                if field_name != 'tags_input':
                    field.widget.attrs['class'] = 'form-control'
    
    def clean_tags_input(self):
        """Convert comma-separated tags to JSON list"""
        tags_input = self.cleaned_data.get('tags_input', '')
        if tags_input:
            # Split by comma, strip whitespace, filter empty strings
            tags_list = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            return tags_list
        return []
    
    def clean_event_date(self):
        """Validate event date"""
        event_date = self.cleaned_data.get('event_date')
        if event_date and event_date < timezone.now().date():
            raise ValidationError("Event date cannot be in the past")
        return event_date
    
    # def clean_event_start_time(self):
    #     """Validate event start time"""
    #     event_date = self.cleaned_data.get('event_date')
    #     event_start_time = self.cleaned_data.get('event_start_time')
        
    #     # If event is today, start time should be in future
    #     if event_date == timezone.now().date() and event_start_time:
    #         current_time = timezone.now().time()
    #         if event_start_time < current_time:
    #             raise ValidationError("Event start time cannot be in the past for today's event")
        
    #     return event_start_time
    
    def clean_event_end_time(self):
        """Validate event end time"""
        event_start_time = self.cleaned_data.get('event_start_time')
        event_end_time = self.cleaned_data.get('event_end_time')
        
        if event_start_time and event_end_time and event_end_time <= event_start_time:
            raise ValidationError("Event end time must be after start time")
        
        return event_end_time
    
    def clean_registration_offer_fee(self):
        """Validate registration offer fee"""
        is_free = self.cleaned_data.get('is_free')
        offer_fee = self.cleaned_data.get('registration_offer_fee')
        
        if is_free and offer_fee and offer_fee > 0:
            raise ValidationError("Offer fee must be 0 for free events")
        
        return offer_fee or 0.00
    
    def clean_registration_strickthrough_fee(self):
        """Validate strickthrough fee"""
        strickthrough_fee = self.cleaned_data.get('registration_strickthrough_fee')
        offer_fee = self.cleaned_data.get('registration_offer_fee')
        
        if strickthrough_fee and offer_fee and strickthrough_fee < offer_fee:
            raise ValidationError("Strickthrough fee cannot be less than offer fee")
        
        return strickthrough_fee
    
    def save(self, commit=True):
        """Save event with tags conversion"""
        # Convert tags_input to tags JSON field
        tags_list = self.cleaned_data.get('tags_input', [])
        self.instance.tags = tags_list
        
        # Set published_at if status changed to published
        if self.instance.pk:
            original = Event.objects.get(pk=self.instance.pk)
            if original.status != 'published' and self.instance.status == 'published':
                self.instance.published_at = timezone.now()
        elif self.instance.status == 'published':
            self.instance.published_at = timezone.now()
        
        return super().save(commit)
    




import re

class EventRegistrationForm(forms.ModelForm):
    """Form for creating and updating event registrations"""
    
    # Event selection with enhanced display
    event = forms.ModelChoiceField(
        queryset=Event.objects.filter(status='published'),
        required=True,
        label="Select Event",
        help_text="Choose a published event",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = EventRegistration
        fields = [
            'event', 'full_name', 'email', 'mobile_number', 'address',
            'payment_status', 'amount_paid', 'special_requirements'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@email.com'
            }),
            'mobile_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '9876543210'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Full address with city, state, and pincode'
            }),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 799.00',
                'step': '0.01'
            }),
            'special_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any special requirements or notes...'
            }),
        }
        help_texts = {
            'mobile_number': 'Enter 10-digit mobile number',
            'amount_paid': 'Amount actually paid by the registrant',
        }
    
    def __init__(self, *args, **kwargs):
        self.event_instance = kwargs.pop('event_instance', None)
        self.is_update = kwargs.pop('is_update', False)
        
        super().__init__(*args, **kwargs)
        
        # If specific event is provided (e.g., registering for a specific event)
        if self.event_instance:
            self.fields['event'].initial = self.event_instance
            self.fields['event'].disabled = True  # Can't change event for specific event registration
        
        # If updating, set initial amount from event if not set
        if self.instance and self.instance.pk:
            if not self.instance.amount_paid and self.instance.event and not self.instance.event.is_free:
                self.fields['amount_paid'].initial = self.instance.event.registration_offer_fee
        
        # Customize queryset for event field
        self.fields['event'].queryset = Event.objects.filter(status='published')
        
        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['event', 'payment_status']:
                if not hasattr(field.widget, 'attrs'):
                    field.widget.attrs = {}
                field.widget.attrs['class'] = 'form-control'
    
    def clean_mobile_number(self):
        """Validate mobile number"""
        mobile_number = self.cleaned_data.get('mobile_number')
        
        if not mobile_number:
            raise ValidationError("Mobile number is required")
        
        # Remove any spaces, dashes, or other characters
        mobile_number = re.sub(r'\D', '', mobile_number)
        
        # Validate mobile number format
        if len(mobile_number) != 10:
            raise ValidationError("Mobile number must be 10 digits")
        
        if not mobile_number.isdigit():
            raise ValidationError("Mobile number should contain only digits")
        
        # Check if this mobile is already registered for the same event
        event = self.cleaned_data.get('event')
        if event:
            existing_reg = EventRegistration.objects.filter(
                event=event,
                mobile_number=mobile_number
            )
            
            # If updating, exclude current instance
            if self.instance and self.instance.pk:
                existing_reg = existing_reg.exclude(pk=self.instance.pk)
            
            if existing_reg.exists():
                raise ValidationError(
                    f"This mobile number is already registered for event '{event.title}'"
                )
        
        return mobile_number
    
    def clean_email(self):
        """Validate email"""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError("Email is required")
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            raise ValidationError("Please enter a valid email address")
        
        return email.lower()
    
    def clean_amount_paid(self):
        """Validate amount paid"""
        amount_paid = self.cleaned_data.get('amount_paid')
        event = self.cleaned_data.get('event')
        payment_status = self.cleaned_data.get('payment_status')
        
        if event:
            if event.is_free:
                if amount_paid and amount_paid > 0:
                    raise ValidationError("Amount paid must be 0 for free events")
                return Decimal('0.00')
            else:
                if payment_status == 'success':
                    if not amount_paid or amount_paid <= 0:
                        raise ValidationError("Amount paid is required for successful payments")
                    if amount_paid > event.registration_offer_fee:
                        raise ValidationError(
                            f"Amount paid cannot exceed event price (₹{event.registration_offer_fee})"
                        )
                elif payment_status == 'pending':
                    if amount_paid and amount_paid > 0:
                        raise ValidationError(
                            "Amount should be 0 for pending payments. "
                            "Set payment status to 'success' if payment is received."
                        )
        
        return amount_paid or Decimal('0.00')
    
    def clean(self):
        """Main validation"""
        cleaned_data = super().clean()
        
        if self.errors:
            return cleaned_data
        
        event = cleaned_data.get('event')
        payment_status = cleaned_data.get('payment_status')
        amount_paid = cleaned_data.get('amount_paid')
        
        # Validate payment status and amount consistency
        if payment_status == 'success' and (not amount_paid or amount_paid <= 0):
            self.add_error('payment_status', 
                "Payment status cannot be 'success' without a payment amount")
        
        # For free events, force payment status to success
        if event and event.is_free:
            cleaned_data['payment_status'] = 'success'
            cleaned_data['amount_paid'] = Decimal('0.00')
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save registration with auto-generated registration ID"""
        # Generate registration ID if not set
        if not self.instance.registration_id:
            import uuid
            self.instance.registration_id = f"REG{str(uuid.uuid4())[:8].upper()}"
        
        # Set amount paid from event if not provided for paid events
        if not self.instance.amount_paid and self.instance.event and not self.instance.event.is_free:
            self.instance.amount_paid = self.instance.event.registration_offer_fee
        
        return super().save(commit)
    



class EventRegistrationBulkForm(forms.Form):
    """Form for bulk registration import"""
    event = forms.ModelChoiceField(
        queryset=Event.objects.filter(status='published'),
        required=True,
        label="Select Event",
        help_text="Choose event for bulk registration",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    csv_file = forms.FileField(
        required=True,
        label="CSV File",
        help_text="Upload CSV file with registrations (columns: full_name, email, mobile_number, address)",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )