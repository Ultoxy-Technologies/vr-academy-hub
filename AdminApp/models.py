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



 

class Enquiry(models.Model):
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    remark = models.TextField(blank=True, null=True)

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
    video_link = models.CharField(blank=True, null=True, help_text="Enter YouTube video link", max_length=255)
  


from django.db import models
from django.conf import settings
from django.utils import timezone
import os

class FreeCourse(models.Model):
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
