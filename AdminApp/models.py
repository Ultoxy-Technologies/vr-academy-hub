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
    is_staff = models.BooleanField(default=True)
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
    def current_price(self):
        """Get current price in paisa for Razorpay"""
        if self.is_free:
            return 0
        return int(self.registration_offer_fee * 100)  # Convert to paisa

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
        return int(float(self.registration_offer_fee or 0) * 100)



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
