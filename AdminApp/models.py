from django.db import models
import os


from django.db import models
from django.utils import timezone

from django.contrib.auth.models import AbstractUser, Group, Permission

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone

from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, mobile_number, email=None, name=None, password=None, **extra_fields):
        if not mobile_number:
            raise ValueError('The Mobile Number must be set')
        email = self.normalize_email(email)
        user = self.model(mobile_number=mobile_number, email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, email=None, name=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(mobile_number, email, name, password, **extra_fields)



class CustomUser(AbstractUser): 

    ROLE_CHOICES = (
        ('is_website_manager', 'Website Manager'),
        ('is_crm_manager', 'CRM Manager'),
        ('is_enrollment', 'Enrollment Manager'),
        ('is_crm_and_enrollment', 'CRM & Enrollment Manager'),
        ('is_staff', 'Staff'),
        ('is_student', 'Student'),
    )
    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default='is_student',
        null=True, blank=True
    )

    username = None
    name = models.CharField(max_length=150)
    dob = models.DateField(verbose_name='Date of Birth', null=True, blank=True)
    dist = models.CharField(max_length=100)
    taluka = models.CharField(max_length=100)
    village = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    action = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['email', 'name']

    objects = CustomUserManager()  # ✅ add this line!

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',
        blank=True
    )

    def __str__(self):
        return self.name or self.mobile_number or "User"


from datetime import timedelta
from django.conf import settings
import random

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='password_otps'
    )
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_otp(length=6):
        """Return a zero-padded numeric OTP as string."""
        return str(random.randint(0, 10**length - 1)).zfill(length)

    def is_valid(self, minutes_valid=10):
        """Return True if OTP was created within `minutes_valid` minutes."""
        return self.created_at + timedelta(minutes=minutes_valid) >= timezone.now()

    def __str__(self):
        return f"OTP({self.user}, {self.otp})"
 

class Enquiry(models.Model):
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    remark = models.TextField(blank=True, null=True)
    is_added_in_CRMFollowup_model = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} ({self.email})"


# Create your models here.
class PhotoGalleryCategories(models.Model):
    category_name = models.CharField(max_length=255) 
 
    def __str__(self):
        return f"{self.category_name}"
    

class PhotoGallery(models.Model):
    category = models.ForeignKey(PhotoGalleryCategories, on_delete=models.CASCADE, related_name='photos')
    caption = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="photo_gallery/")
    is_show_on_home_page = models.BooleanField(null=True)

    def delete(self, *args, **kwargs):
        # Delete the image file from the filesystem
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super(PhotoGallery, self).delete(*args, **kwargs)

    def __str__(self):
        return f"{self.caption} Image"

class VideoGallery(models.Model): 
    caption = models.CharField(max_length=255, blank=True, null=True)
    video_link = models.CharField(blank=True, null=True, help_text="Enter YouTube video link", max_length=500)
  

 
 

class Certificate(models.Model):
 
    title = models.CharField(
        max_length=255,
        help_text="Name of the certificate or recognition title"
    )
    issued_by = models.CharField(
        max_length=255,
        help_text="Organization or institution that issued the certificate"
    )
    issued_to = models.CharField(
        max_length=255,
        help_text="Name of the recipient"
    )
    issue_date = models.DateField(
        help_text="Date when the certificate was issued"
    )
    description = models.TextField(
        blank=True,
        help_text="Short description about the certificate or award (optional)"
    )
    image = models.ImageField(
        upload_to="certificates/",
        blank=True,
        null=True,
        help_text="Upload the certificate image"
    )
    tag = models.CharField(
        max_length=50,
        default="Verified",
        help_text="Short label such as Verified, Awarded, Achieved, etc."
    )
    rating = models.PositiveSmallIntegerField(
        default=5,
        help_text="Star rating (1–5) for the recognition"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this certificate from the website"
    )

    class Meta:
        ordering = ['-issue_date']
        verbose_name = "Certificate / Award"
        verbose_name_plural = "Certificates & Awards"

    def __str__(self):
        return f"{self.title}"




class Basic_to_Advance_Cource(models.Model):
    new_batch_start_slug = models.CharField( help_text="e.g. New Batch Start", max_length=20,null=True, blank=True)
    title = models.CharField(max_length=255)
    event_date = models.CharField(max_length=100, help_text="e.g. 25 October (Saturday)")
    time = models.CharField(max_length=50, help_text="e.g. 06:00 PM")
    duration = models.CharField(max_length=50, help_text="e.g. 2 Months")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    total_reviews = models.CharField(max_length=50, help_text="e.g. 16k+")
    offer_price = models.CharField(max_length=20, default="Free")
    original_price = models.CharField(max_length=20, blank=True, null=True)
    thumbnail = models.ImageField(upload_to="course_thumbnails/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.title} ({self.event_date})"

class Advance_to_Pro_Cource(models.Model):
    new_batch_start_slug = models.CharField( help_text="e.g. New Batch Start", max_length=20,null=True, blank=True)
    title = models.CharField(max_length=255)
    event_date = models.CharField(max_length=100, help_text="e.g. 25 October (Saturday)")
    time = models.CharField(max_length=50, help_text="e.g. 06:00 PM")
    duration = models.CharField(max_length=50, help_text="e.g. 2 Months")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    total_reviews = models.CharField(max_length=50, help_text="e.g. 16k+")
    offer_price = models.CharField(max_length=20, default="Free")
    original_price = models.CharField(max_length=20, blank=True, null=True)
    thumbnail = models.ImageField(upload_to="course_thumbnails/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.event_date})"
    
    


from django.db import models
from django.conf import settings
from django.utils import timezone
import os

class FreeCourse(models.Model):
    duration=models.CharField(null=True,blank=True, max_length=50, help_text="ex.15 Days, 2 Months, 45 min")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video = models.FileField(upload_to='free_courses/videos/')
    is_active = models.BooleanField(default=True)
    thumbnail= models.ImageField(upload_to='free_courses/thumbnails/', blank=True, null=True)
    certificate_template = models.FileField(
        upload_to='free_courses/certificates/',
        blank=True,
        null=True,
        help_text="Template to generate certificate after course completion"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        """Delete video and certificate files from filesystem when course is deleted."""
        if self.video and os.path.isfile(self.video.path):
            os.remove(self.video.path)
        if self.certificate_template and os.path.isfile(self.certificate_template.path):
            os.remove(self.certificate_template.path)
        super().delete(*args, **kwargs)


class FreeCourseProgress(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use your CustomUser
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(FreeCourse, on_delete=models.CASCADE)
    watched_duration = models.PositiveIntegerField(default=0, help_text="Seconds watched")
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} - {self.course.title} - {'Completed' if self.completed else 'In Progress'}"

    def mark_completed(self):
        """Mark course as completed and save timestamp."""
        self.completed = True
        self.completed_at = timezone.now()
        self.save()

    @property
    def certificate_ready(self):
        """
        Returns True if the course is completed and certificate is available.
        This is useful for template logic to allow downloads.
        """
        return self.completed and bool(self.course.certificate_template)





from django.db import models
from django.contrib.auth.models import User
import uuid

class Event(models.Model):
    EVENT_STATUS = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    # Thumbnail
    thumbnail = models.ImageField(
        upload_to="event_thumbnails/",
        blank=True,
        null=True,
        help_text="Upload event thumbnail image (Recommended size: 800x600 pixels)"
    )

    # Basic event information
    title = models.CharField(
        max_length=200,
        help_text="Enter the main title of the event"
    )
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text="Add an optional subtitle for the event"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Write a detailed description of the event"
    )

    # Event categorization
    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Specify the category or type of event (e.g., Webinar, Workshop)"
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        null=True,  
        help_text="List of keywords related to the event (e.g., ['Technology', 'Education'])"
    )

    # Event timing
    event_date = models.DateField(
        help_text="Select the event date"
    )
    event_start_time = models.TimeField(
        help_text="Enter the start time of the event"
    )
    event_end_time = models.TimeField(
        help_text="Enter the end time of the event"
    )
    timezone = models.CharField(
        max_length=50,
        default='IST',
        help_text="Specify the event timezone"
    )

    # Meeting details
    meeting_link = models.URLField(
        blank=True,
        null=True,
        help_text="Add meeting link if applicable (e.g., Zoom or Google Meet URL)"
    )
    meeting_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Enter meeting ID if required"
    )
    meeting_password = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Enter meeting password if required"
    )

    # Pricing
    is_free = models.BooleanField(
        default=False,
        help_text="Check if the event is free to attend"
    )
    registration_strickthrough_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Enter original registration fee (for strikethrough display)"
    )

    registration_offer_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Enter discounted or current registration fee"
    )

    # Status and metadata
    status = models.CharField(
        max_length=20,
        choices=EVENT_STATUS,
        default='draft',
        help_text="Select current event status"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Automatically set when event is created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Automatically updates when event is modified"
    )
    published_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date and time when event was published"
    )

    def __str__(self):
        return self.title

 
    @property
    def display_price(self):
        """Get display price"""
        if self.is_free:
            return "FREE"
        return f"₹{self.registration_offer_fee}"
    
    @property
    def current_price(self):
        """
        Returns price in paisa (integer) as required by Razorpay.
        """
        if self.is_free:
            return 0
        # Ensure we have a valid decimal value
        fee = self.registration_offer_fee or 0
        if isinstance(fee, Decimal):
            return int(fee * 100)
        return int(float(fee) * 100)



import uuid
from django.db import models

class EventRegistration(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    # Registration Information
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    registration_id = models.CharField(max_length=20, unique=True, blank=True)
    
    # Personal Information
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    
    # Payment Information
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending'
    )
    
    # Additional Information
    special_requirements = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Event Registration"
        verbose_name_plural = "Event Registrations"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.event.title}"

    def save(self, *args, **kwargs):
        if not self.registration_id:
            # Generate a unique registration ID
            self.registration_id = f"REG{str(uuid.uuid4())[:8].upper()}"
        if not self.amount_paid and not self.event.is_free:
            self.amount_paid = self.event.registration_offer_fee
        super().save(*args, **kwargs)

    def generate_registration_id(self):
        """Generate a unique registration ID"""
        return f"REG{str(uuid.uuid4())[:8].upper()}"
    




class CRM_Student_Interested_for_options(models.Model):
    interest_option = models.CharField(max_length=50)
    def __str__(self):
        return self.interest_option
   
class Branch(models.Model):
    branch_name = models.CharField(max_length=50)
    def __str__(self):
        return self.branch_name

from simple_history.models import HistoricalRecords

class CRMFollowup(models.Model):
    # ================== Choices ==================
    PRIORITY_CHOICES = [
        ('high', 'High Priority'),
        ('medium', 'Medium Priority'),
        ('low', 'Low Priority'),
    ]

    STATUS = [
        ('interested', 'Interested'),
        ('planning', 'Planning'),
        ('under_review', 'Under Review'),
        ('on_hold', 'On Hold'),
        ('class_joined', 'Class Joined'),
        ('class_completed', 'Class Completed'),
        ('not_interested', 'Not Interested'),
    ]

    CALL_RESPONSE_CHOICES = [
        ('answered', 'Answered'),
        ('not_answered', 'Not Answered'),
        ('busy', 'Busy'),
        ('switched_off', 'Switched Off'),
    ]

    SOURCE_CHOICES = [
        ('website', 'Website'),
        ('instagram', 'Instagram'),
        ('whatsapp', 'WhatsApp'),
        ('walkin', 'Walk-in'),
        ('reference', 'Reference'),
    ]
    
    # ================== Student Info ==================
    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    student_interested_for = models.ForeignKey(
        CRM_Student_Interested_for_options,
        on_delete=models.CASCADE, null=True, blank=True
    )
    source = models.CharField(
        max_length=30,
        choices=SOURCE_CHOICES,
        default='website', null=True, blank=True
    )

    address = models.CharField(
        max_length=100,   null=True, blank=True
    )

    # ================== Lead Status ==================
    status = models.CharField(
        max_length=30,
        choices=STATUS,
        default='interested', null=True, blank=True
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium', null=True, blank=True
    )

    # ================== Follow-Up Details ==================
    follow_up_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='crm_tasks', 
        null=True, blank=True
    )
     
        
    # ================== Follow-Up Details ==================
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='crm_branch',
        null=True, blank=True
    )
    
    call_response = models.CharField(
        max_length=20,
        choices=CALL_RESPONSE_CHOICES, null=True, blank=True
    )
    follow_up_date = models.DateTimeField(blank=True, null=True)
    next_followup_reminder = models.DateTimeField(blank=True, null=True)
    follow_up_notes = models.TextField(blank=True, null=True)

    # ================== Class Info ==================
    class_start_date = models.DateTimeField(blank=True, null=True)

    # ================== System Fields ==================
    created_at = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['follow_up_date']),
            models.Index(fields=['next_followup_reminder']),
        ]
        
    def __str__(self):
        return f"{self.name} - {self.mobile_number}"

 

from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError
# models.py - Add these methods to your existing Batch model
class Batch(models.Model):
    """Batch/Class for a specific course"""
    BATCH_STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    batch_code = models.CharField(max_length=20, unique=True)
    batch_title = models.CharField(max_length=100)
    batch_status = models.CharField(max_length=20, choices=BATCH_STATUS_CHOICES, default='upcoming')
    
    # Course selection
    basic_to_advance_cource = models.ForeignKey(
        'Basic_to_Advance_Cource', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    advance_to_pro_cource = models.ForeignKey(
        'Advance_to_Pro_Cource', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Capacity
    max_students = models.PositiveIntegerField(default=30)
    description = models.TextField(blank=True, help_text="Batch description and details")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Batches"
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.batch_code} - {self.batch_title}"
    
    def clean(self):
        """Validate batch data"""
        # Ensure at least one course is selected
        if not self.basic_to_advance_cource and not self.advance_to_pro_cource:
            raise ValidationError("Please select at least one course.")
        
        # Ensure not both courses are selected
        if self.basic_to_advance_cource and self.advance_to_pro_cource:
            raise ValidationError("Cannot select both courses.")
        
        # Validate dates
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError("Batch start date cannot be after end date.")
        
        # Validate max students
        if self.max_students <= 0:
            raise ValidationError("Maximum students must be greater than 0.")
        
        # Auto-update batch status based on dates
        # self.update_batch_status()
    
    def save(self, *args, **kwargs):
        # Auto-update batch status
        # self.update_batch_status()
        super().save(*args, **kwargs)
    
    # def update_batch_status(self):
    #     """Update batch status based on current date"""
    #     from django.utils import timezone
        
    #     today = timezone.now().date()
        
    #     if self.batch_status == 'cancelled':
    #         return  # Don't change cancelled batches
        
    #     if self.start_date > today:
    #         self.batch_status = 'upcoming'
    #     elif self.end_date and self.end_date < today:
    #         self.batch_status = 'completed'
    #     elif self.start_date <= today:
    #         self.batch_status = 'ongoing'
    
    @property
    def course(self):
        """Get the selected course"""
        return self.basic_to_advance_cource or self.advance_to_pro_cource
    
    @property
    def course_type(self):
        """Get course type"""
        if self.basic_to_advance_cource:
            return "Basic to Advance"
        elif self.advance_to_pro_cource:
            return "Advance to Pro"
        return "Not Selected"
    
    @property
    def course_fees(self):
        """Get course fees"""
        if self.course and hasattr(self.course, 'original_price'):
            try:
                price_str = str(self.course.original_price).replace(',', '').replace('₹', '').strip()
                return Decimal(price_str) if price_str else Decimal('0.00')
            except:
                return Decimal('0.00')
        return Decimal('0.00')
    
    @property
    def current_students(self):
        """Number of currently enrolled students"""
        return self.enrollments.filter(status='active').count()
    
    @property
    def total_students(self):
        """Total students ever enrolled"""
        return self.enrollments.count()
    
    @property
    def available_seats(self):
        """Available seats in batch"""
        return max(self.max_students - self.current_students, 0)
    
    @property
    def occupancy_percentage(self):
        """Percentage of seats occupied"""
        if self.max_students == 0:
            return 0
        return (self.current_students / self.max_students) * 100
    
    @property
    def duration_days(self):
        """Batch duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0
    
    @property
    def days_remaining(self):
        """Days remaining for batch completion"""
        from django.utils import timezone
        
        if not self.end_date or self.end_date < timezone.now().date():
            return 0
        
        return (self.end_date - timezone.now().date()).days
    
    @property
    def is_full(self):
        """Check if batch is full"""
        return self.current_students >= self.max_students
    
    @property
    def can_enroll(self):
        """Check if new students can enroll"""
        return (
            self.is_active and 
            not self.is_full and 
            self.batch_status in ['upcoming', 'ongoing']
        )
    
    
class Enrollment(models.Model):
    """Main enrollment record - One student can enroll in multiple batches"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('discontinued', 'Discontinued'),
        ('on_hold', 'On Hold'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Payment Pending'),
        ('partial', 'Partial Payment'),
        ('completed', 'Payment Completed'),
        ('overdue', 'Payment Overdue'),
    ]
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='enrollments')
    
    enrollment_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Course info
    course_title = models.CharField(max_length=255, blank=True, editable=False)
    
    # Fees
    total_fees = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_fees = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    # Dates
    class_start_date = models.DateField(null=True, blank=True)
    class_end_date = models.DateField(null=True, blank=True)
    
    # Payment schedule (simple text field for reference)
    payment_schedule = models.TextField(blank=True, help_text="e.g., 5000 on 10th Dec, 5000 on 10th Jan")
        
    # ================== Follow-Up Details ==================
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='enrollment_branch',
        null=True, blank=True
    )    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    
    class Meta:
        unique_together = ['student', 'batch']
        ordering = ['-enrollment_date']
    
    def clean(self):
        """Validate enrollment data"""
        if self.discount > self.total_fees:
            raise ValidationError("Discount cannot exceed total fees.")
    
    def save(self, *args, **kwargs):
        # Auto-set fees from batch if not provided
        if not self.total_fees and self.batch:
            self.total_fees = self.batch.course_fees
        
        # Auto-set course title from batch
        if self.batch:
            if self.batch.basic_to_advance_cource:
                self.course_title = self.batch.basic_to_advance_cource.title
            elif self.batch.advance_to_pro_cource:
                self.course_title = self.batch.advance_to_pro_cource.title
        
        # Auto-set dates from batch if not provided
        if not self.class_start_date and self.batch:
            self.class_start_date = self.batch.start_date
        if not self.class_end_date and self.batch and self.batch.end_date:
            self.class_end_date = self.batch.end_date
        
        # Calculate net fees
        self.net_fees = self.total_fees - self.discount
        
        # Update payment status based on paid amount
        self.update_payment_status()
        
        super().save(*args, **kwargs)
    
    def update_payment_status(self):
        """Update payment status based on paid amount"""
        if not self.pk:
            return  # Don't update for new objects
        
        if self.paid_amount >= self.net_fees:
            self.payment_status = 'completed'
        elif self.paid_amount > 0:
            self.payment_status = 'partial'
        else:
            self.payment_status = 'pending'
        
        # Check for overdue payments using date comparison directly
        from django.utils import timezone
        today = timezone.now().date()
        
        # Find payments with due_date in the past and no payment_date
        # OR payment_date after due_date
        overdue_payments = self.payments.filter(
            due_date__isnull=False
        ).filter(
            models.Q(payment_date__isnull=True, due_date__lt=today) |
            models.Q(payment_date__isnull=False, payment_date__gt=models.F('due_date'))
        ).exists()
        
        if overdue_payments and self.payment_status != 'completed':
            self.payment_status = 'overdue'
    
    def __str__(self):
        return f"{self.student.name} - {self.batch.batch_title}"
    
    @property
    def paid_amount(self):
        """Total paid amount"""
        try:
            # Aggregate payments for this enrollment
            result = self.payments.aggregate(total=models.Sum('amount'))
            total = result['total']
            return total if total is not None else Decimal('0.00')
        except Exception:
            return Decimal('0.00')
    
    @property
    def balance(self):
        """Remaining balance"""
        return max(self.net_fees - self.paid_amount, Decimal('0.00'))
    
    @property
    def is_fully_paid(self):
        """Check if all fees are paid"""
        return self.paid_amount >= self.net_fees
    
    @property
    def payment_progress(self):
        """Payment progress percentage"""
        if not self.net_fees or self.net_fees <= 0:
            return 100
        try:
            progress = (self.paid_amount / self.net_fees) * 100
            return min(progress, 100)
        except (ZeroDivisionError, TypeError):
            return 0
    
    @property
    def total_payments(self):
        """Total number of payments"""
        return self.payments.count()
    
    @property
    def last_payment(self):
        """Get last payment"""
        return self.payments.order_by('-payment_date').first()
    
    @property
    def first_payment(self):
        """Get first payment"""
        return self.payments.order_by('payment_date').first()
    
    @property
    def payment_dates(self):
        """Get all payment dates"""
        return list(self.payments.values_list('payment_date', flat=True))
    
    @property
    def can_issue_certificate(self):
        """Check if certificate can be issued"""
        return self.status == 'completed' and self.is_fully_paid
    
    @property
    def enrollment_id(self):
        """Generate enrollment ID"""
        if self.pk:
            return f"ENR-{str(self.pk).zfill(6)}"
        return "ENR-NEW"
    
class Payment(models.Model):
    """Single model for all payments - Flexible system"""
    PAYMENT_TYPE_CHOICES = [
        ('admission', 'Admission Fee'),
        ('installment', 'Installment'),
        ('full', 'Full Payment'),
        ('partial', 'Partial Payment'),
        ('other', 'Other'),
    ]
    
    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('online', 'Online'),
        ('cheque', 'Cheque'),
        ('upi', 'UPI'),
        ('card', 'Card'),
    ]
    
    # Payment ID for reference
    payment_id = models.CharField(max_length=20, unique=True, editable=False)
    
    # Link to enrollment
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='installment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES)
    
    # Installment info (optional, for tracking)
    installment_number = models.PositiveIntegerField(null=True, blank=True, help_text="e.g., 1 for first installment")
    due_date = models.DateField(null=True, blank=True, help_text="Due date for this payment")
    
    # Payment reference
    reference_number = models.CharField(max_length=100, blank=True)
    
    # Who received it
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='received_payments'
    )
    
    remarks = models.TextField(blank=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    
    class Meta:
        ordering = ['-payment_date']
    
    def clean(self):
        """Validate payment data"""
        if not self.amount:
            raise ValidationError("Payment amount is required.")
        if self.amount <= 0:
            raise ValidationError("Payment amount must be greater than 0.")
        
        if self.payment_date > timezone.now().date():
            raise ValidationError("Payment date cannot be in the future.")
        
        # Validate installment number if provided
        if self.installment_number is not None and self.installment_number <= 0:
            raise ValidationError("Installment number must be positive.")
    
    def save(self, *args, **kwargs):
        # Generate payment ID if new
        if not self.payment_id:
            prefix = "PAY"
            year_month = timezone.now().strftime("%Y%m")
            count = Payment.objects.filter(
                payment_id__startswith=f"{prefix}-{year_month}-"
            ).count()
            self.payment_id = f"{prefix}-{year_month}-{count+1:04d}"
        
        super().save(*args, **kwargs)
        
        # Update enrollment payment status after saving
        if self.enrollment:
            self.enrollment.update_payment_status()
            self.enrollment.save()
    
    def __str__(self):
        type_display = self.get_payment_type_display()
        return f"{self.payment_id} - ₹{self.amount} - {type_display}"
    
    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        if self.due_date:
            if self.payment_date:
                return self.payment_date > self.due_date
            else:
                return self.due_date < timezone.now().date()
        return False
    
    @property
    def days_overdue(self):
        """Days overdue"""
        if not self.is_overdue:
            return 0
        if self.payment_date:
            overdue_date = max(self.due_date, self.payment_date)
        else:
            overdue_date = self.due_date
        return (timezone.now().date() - overdue_date).days
    
    @property
    def is_installment(self):
        """Check if this is an installment payment"""
        return self.payment_type == 'installment'
    
    @property
    def is_admission(self):
        """Check if this is an admission payment"""
        return self.payment_type == 'admission'
    
    @property
    def payment_month(self):
        """Get payment month for reporting"""
        return self.payment_date.strftime('%B %Y')
    


class StudentCertificate(models.Model):
    """Certificate issued upon course completion"""
    enrollment = models.OneToOneField(
        Enrollment, 
        on_delete=models.CASCADE, 
        related_name='certificate'
    )
    
    certificate_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField(default=timezone.now)
    file = models.FileField(upload_to='certificates/', blank=True, null=True)
    
    def __str__(self):
        return f"Certificate {self.certificate_number}"
    
    def clean(self):
        """Validate certificate data"""
        if self.enrollment.status != 'completed':
            raise ValidationError("Certificate can only be issued for completed enrollments.")
        
        if not self.enrollment.is_fully_paid:
            raise ValidationError("Certificate can only be issued when all fees are paid.")
    
    def save(self, *args, **kwargs):
        if not self.certificate_number:
            import random
            self.certificate_number = f"CERT-{self.enrollment.id}-{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)