from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html, mark_safe
from .models import PhotoGalleryCategories, PhotoGallery, VideoGallery, CustomUser, FreeCourse, FreeCourseProgress, Enquiry,EventRegistration,Event,Basic_to_Advance_Cource,Advance_to_Pro_Cource,Certificate

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone', 'email']
    search_fields = ['full_name', 'phone', 'email']




# -----------------------------
# Custom user 
# -----------------------------
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserChangeForm, CustomUserCreationForm

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser

    list_display = ['profile_image_preview', 'name', 'mobile_number', 'email', 'role', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['name', 'mobile_number', 'email']
    ordering = ['-date_joined']

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="38" height="38" style="object-fit:cover; border-radius:50%; border:1.5px solid #6366F1;" />', obj.profile_image.url)
        initial = (obj.name[0] if obj.name else obj.mobile_number[0] if obj.mobile_number else 'U').upper()
        return format_html('<div style="width:38px; height:38px; border-radius:50%; background:#EEF2FF; color:#4F46E5; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:15px; border:1px solid #C7D2FE;">{}</div>', initial)
    profile_image_preview.short_description = "Photo"

    def get_ordering(self, request):
        return ['-date_joined']

    fieldsets = (
        (None, {'fields': ('mobile_number', 'password')}),
        ('Personal Info', {
            'fields': (
                'profile_image',
                'name',
                'email',
                'role',
                'dob',
                'dist',
                'taluka',
                'village',
                'action',
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
            'classes': ('collapse',),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile_number', 'name', 'profile_image', 'email', 'role', 'password1', 'password2'),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions')

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_users.short_description = "Deactivate selected users"
    
    actions = ['activate_users', 'deactivate_users']

admin.site.register(CustomUser, CustomUserAdmin)

# -----------------------------
# INLINE for Photos under Category
# -----------------------------
class PhotoGalleryInline(admin.TabularInline):
    model = PhotoGallery
    extra = 1
    fields = ('image_preview', 'caption', 'description', 'image', 'is_show_on_home_page')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="70" style="object-fit:cover; border-radius:6px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Preview"


# -----------------------------
# CATEGORY ADMIN
# -----------------------------
@admin.register(PhotoGalleryCategories)
class PhotoGalleryCategoriesAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'total_photos')
    search_fields = ('category_name',)
    inlines = [PhotoGalleryInline]

    def total_photos(self, obj):
        return obj.photos.count()
    total_photos.short_description = "No. of Photos"


# -----------------------------
# PHOTO GALLERY ADMIN
# -----------------------------
@admin.register(PhotoGallery)
class PhotoGalleryAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'caption', 'category', 'is_show_on_home_page')
    list_filter = ('category', 'is_show_on_home_page')
    search_fields = ('caption', 'category__category_name')
    readonly_fields = ('image_preview',)
    list_editable = ('is_show_on_home_page',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'caption', 'description')
        }),
        ('Media', {
            'fields': ('image_preview', 'image')
        }),
        ('Display Settings', {
            'fields': ('is_show_on_home_page',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="100" style="object-fit:cover; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.2);" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Preview"


# -----------------------------
# VIDEO GALLERY ADMIN
# ----------------------------- 
import re
from django.contrib import admin
from django.utils.html import format_html


@admin.register(VideoGallery)
class VideoGalleryAdmin(admin.ModelAdmin):
    list_display = ('caption', 'video_link', 'thumbnail_preview')
    search_fields = ('caption', 'video_link')
    list_per_page = 20

    readonly_fields = ('thumbnail_display',)

    fieldsets = (
        ('Video Details', {
            'fields': ('caption', 'video_link')
        }),
        ('Preview', {
            'fields': ('thumbnail_display',),
            'description': 'Click on the thumbnail to open the YouTube video.'
        }),
    )

    def thumbnail_display(self, obj):
        """Show YouTube thumbnail that opens YouTube when clicked."""
        if not obj.video_link:
            return "No video link provided."

        video_id = self.extract_youtube_id(obj.video_link)
        if video_id:
            # YouTube thumbnail URLs
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            
            return format_html(
                '<a href="{}" target="_blank" style="text-decoration: none; display: inline-block;">'
                '<img src="{}" width="360" height="200" style="border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.2); border: 1px solid #ddd; cursor: pointer;" '
                'alt="YouTube Thumbnail" title="Click to watch on YouTube">'
                '<div style="text-align: center; margin-top: 8px; color: #666; font-size: 12px;">Click thumbnail to watch video</div>'
                '</a>',
                youtube_url, thumbnail_url
            )
        return "Invalid or unsupported YouTube link."
    thumbnail_display.short_description = "Video Thumbnail"

    def extract_youtube_id(self, url):
        """Extracts YouTube video ID from various URL formats."""
        if not url:
            return None
            
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtube\.com/embed/|youtube\.com/v/)([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch/([a-zA-Z0-9_-]{11})',
            r'[?&]v=([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def thumbnail_preview(self, obj):
        """For list_display column preview (small thumbnail version)."""
        if obj and obj.video_link:
            video_id = self.extract_youtube_id(obj.video_link)
            if video_id:
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                
                return format_html(
                    '<a href="{}" target="_blank" title="Click to watch on YouTube">'
                    '<img src="{}" width="120" height="80" style="border-radius:4px; border: 1px solid #ddd; cursor: pointer;">'
                    '</a>',
                    youtube_url, thumbnail_url
                )
        return "—"
    thumbnail_preview.short_description = "Thumbnail"


# ----------------------------
# FreeCourseProgress Inline (SIMPLIFIED - No custom fields)
# ----------------------------
class FreeCourseProgressInline(admin.TabularInline):
    model = FreeCourseProgress
    extra = 0
    can_delete = False
    verbose_name = "Student Progress"
    verbose_name_plural = "Students Progress"
    max_num = 0
    
    # Only use actual model fields (no custom methods)
    fields = ('student', 'watched_duration', 'completed', 'completed_at')
    readonly_fields = ('student', 'watched_duration', 'completed', 'completed_at')


# ----------------------------
# FreeCourse Admin
# ----------------------------
@admin.register(FreeCourse)
class FreeCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'created_at', 'video_link', 'certificate_link', 'is_active')
    search_fields = ('title', 'description')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at',)
    inlines = [FreeCourseProgressInline]
    
    fieldsets = [
        ('Course Information', {
            'fields': ['title', 'duration', 'description', 'is_active']
        }),
        ('Media Files', {
            'fields': ['video', 'thumbnail', 'certificate_template'],
            'classes': ['collapse']
        }),
    ]

    def video_link(self, obj):
        if obj.video:
            return format_html(
                '<a href="{}" target="_blank" style="display:inline-block; padding:5px 10px; background:#007bff; color:white; border-radius:3px; text-decoration:none;">'
                '📺 View Video'
                '</a>',
                obj.video.url
            )
        return "-"
    video_link.short_description = "Video"

    def certificate_link(self, obj):
        if obj.certificate_template:
            return format_html(
                '<a href="{}" target="_blank" style="display:inline-block; padding:5px 10px; background:#28a745; color:white; border-radius:3px; text-decoration:none;">'
                '📄 Certificate'
                '</a>',
                obj.certificate_template.url
            )
        return "-"
    certificate_link.short_description = "Certificate"


# ----------------------------
# FreeCourseProgress Admin (Separate page with formatted displays)
# ----------------------------
@admin.register(FreeCourseProgress)
class FreeCourseProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'formatted_duration', 'completion_status', 'completion_date', 'certificate_status')
    list_filter = ('completed', 'course', 'completed_at')
    search_fields = ('student__name', 'student__mobile_number', 'course__title')
    readonly_fields = ('student', 'course', 'watched_duration', 'completed', 'completed_at')
    
    fieldsets = [
        ('Student Information', {
            'fields': ['student', 'course']
        }),
        ('Progress Details', {
            'fields': ['watched_duration', 'completed', 'completed_at']
        }),
    ]

    def formatted_duration(self, obj):
        """Format seconds into minutes:seconds"""
        if obj.watched_duration:
            minutes = obj.watched_duration // 60
            seconds = obj.watched_duration % 60
            return f"{minutes}m {seconds}s"
        return "0s"
    formatted_duration.short_description = "Watched Duration"
    formatted_duration.admin_order_field = 'watched_duration'

    def completion_status(self, obj):
        """Display completion status with colors"""
        if obj.completed:
            return mark_safe('<span style="color: green; font-weight: bold;">✓ Completed</span>')
        return mark_safe('<span style="color: orange;">In Progress</span>')
    completion_status.short_description = "Status"
    completion_status.admin_order_field = 'completed'

    def completion_date(self, obj):
        """Format completion date"""
        if obj.completed_at:
            return obj.completed_at.strftime("%Y-%m-%d %H:%M")
        return "-"
    completion_date.short_description = "Completed At"
    completion_date.admin_order_field = 'completed_at'

    def certificate_status(self, obj):
        """Show certificate availability"""
        if obj.certificate_ready:
            return mark_safe('<span style="color: green; font-weight: bold;">✓ Available</span>')
        return mark_safe('<span style="color: #666;">Not Available</span>')
    certificate_status.short_description = "Certificate"

# ----------------------------
# Shared Admin Base Class
# ----------------------------
class CourseBaseAdmin(admin.ModelAdmin):
    list_display = (
        'thumbnail_preview',
        'title',
        'event_date',
        'time',
        'duration',
        'rating',
        'total_reviews',
        'offer_price',
        'original_price',
        'is_active',
    )
    list_filter = ('is_active', 'duration', 'rating')
    search_fields = ('title', 'event_date', 'duration', 'offer_price')
    list_editable = ('is_active',)
    ordering = ('-event_date',)
    list_per_page = 25

    fieldsets = (
        ('Course Details', {
            'fields': ('title', 'event_date', 'time', 'duration', 'rating', 'total_reviews','new_batch_start_slug')
        }),
        ('Pricing Information', {
            'fields': ('offer_price', 'original_price')
        }),
        ('Media', {
            'fields': ('thumbnail',)  # Removed thumbnail_preview
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def thumbnail_preview(self, obj):
        """Display image preview in admin."""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="height:70px; border-radius:10px; box-shadow:0 0 5px rgba(0,0,0,0.3);"/>',
                obj.thumbnail.url
            )
        return format_html('<span style="color:{};">{}</span>', 'gray', 'No Image')
    thumbnail_preview.short_description = "Thumbnail"

    def get_queryset(self, request):
        """Enhance query performance."""
        return super().get_queryset(request).only(
            'title', 'event_date', 'time', 'duration', 'rating',
            'total_reviews', 'offer_price', 'original_price', 'thumbnail', 'is_active'
        )

    # This is optional - only needed if you want the preview in the change form
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        """Dynamically set readonly fields."""
        if obj:  # If editing an existing object
            return ('thumbnail_preview',)  # Add preview only when editing
        return ()  # Empty when creating new object


# ----------------------------
# Register Basic_to_Advance_Cource
# ----------------------------
@admin.register(Basic_to_Advance_Cource)
class BasicToAdvanceCourseAdmin(CourseBaseAdmin):
    list_display = CourseBaseAdmin.list_display + ()
    list_filter = CourseBaseAdmin.list_filter + ('event_date',)
    search_fields = CourseBaseAdmin.search_fields + ('event_date',)

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)  # Optional for Jazzmin styling
        }


# ----------------------------
# Register Advance_to_Pro_Cource
# ----------------------------
@admin.register(Advance_to_Pro_Cource)
class AdvanceToProCourseAdmin(CourseBaseAdmin):
    list_display = CourseBaseAdmin.list_display + ()
    list_filter = CourseBaseAdmin.list_filter + ('event_date',)
    search_fields = CourseBaseAdmin.search_fields + ('event_date',)

 
# ----------------------------
# Certificate ADMIN
# ----------------------------
from django.contrib import admin
from .models import Certificate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ( 'title', 'issued_by', 'issued_to', 'issue_date', 'rating', 'is_active')
    list_filter = ('issued_by', 'is_active', 'issue_date')
    search_fields = ( 'title', 'issued_by', 'issued_to')
    list_editable = ('is_active',) 
    fieldsets = (
        ('Certificate Info', {
            'fields': ( 'title', 'issued_by', 'issued_to', 'issue_date', 'description')
        }),
        ('Media & Tags', {
            'fields': ('image', 'tag', 'rating')
        }),
        ('Visibility', {
            'fields': ('is_active',)
        }),
    )

from django.contrib import admin
from django import forms
from django.utils import timezone


# ✅ Custom form with HTML5 Date/Time widgets (shows clock UI)
class EventAdminForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
            'event_start_time': forms.TimeInput(attrs={'type': 'time'}),
            'event_end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm  # ✅ Connect custom form

    # Displayed columns in list view
    list_display = (
        'title',
        'category',
        'event_date',
        'event_start_time',
        'status',
        'is_free',
        'registration_offer_fee',
        'created_at',
    )

    search_fields = ('title', 'category', 'tags')
    list_filter = ('status', 'is_free', 'category', 'event_date')
    ordering = ('-event_date',)
    readonly_fields = ('created_at', 'updated_at', 'published_at')

    fieldsets = (
        ('📸 Thumbnail', {
            'fields': ('thumbnail',),
            'description': 'Upload a thumbnail image to represent this event visually.'
        }),
        
        ('📝 Basic Information', {
            'fields': ('title', 'subtitle', 'description'),
            'description': 'Enter the title, subtitle, and full description for this event.'
        }),
        
        ('🏷️ Categorization', {
            'fields': ('category', 'tags'),
            'description': 'Classify the event using categories and relevant tags.'
        }),
        
        ('⏰ Event Timing', {
            'fields': ('event_date', 'event_start_time', 'event_end_time', 'timezone'),
            'description': 'Specify when the event will take place.'
        }),
        
        ('💻 Meeting Details (Optional)', {
            'fields': ('meeting_link', 'meeting_id', 'meeting_password'),
            'description': 'If the event is virtual, include the online meeting information here.'
        }),
        
        ('💰 Pricing Details', {
            'fields': ('is_free', 'registration_strickthrough_fee', 'registration_offer_fee'),
            'description': 'Set pricing options for registration. Leave as free if applicable.'
        }),
        
        ('⚙️ Status & Metadata', {
            'fields': ('status', 'published_at', 'created_at', 'updated_at'),
            'description': 'Manage event status and system timestamps.'
        }),
    )

    def save_model(self, request, obj, form, change):
        """Automatically set published_at when event is marked as published."""
        if obj.status == 'published' and not obj.published_at:
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)






from django.contrib import admin
from django.db.models import DecimalField
from .models import EventRegistration

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['registration_id', 'full_name', 'email', 'payment_status', 'created_at']
    list_filter = ['payment_status']
    search_fields = ['registration_id', 'full_name', 'email']
    readonly_fields = ['registration_id', 'created_at', 'updated_at']
 
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.contrib import messages
from .models import CRM_Student_Interested_for_options, CRMFollowup, Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch_name')
    search_fields = ('branch_name',)
    ordering = ('id',)


@admin.register(CRM_Student_Interested_for_options)
class CRM_Student_Interested_for_optionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'interest_option')
    search_fields = ('interest_option',)
    ordering = ('interest_option',)


@admin.register(CRMFollowup)
class CRMFollowupAdmin(admin.ModelAdmin):
    change_list_template = "admin/AdminApp/crmfollowup/change_list.html"

    list_display = (
        'id',
        'name',
        'mobile_number',
        'status_badge',
        'priority_badge',
        'student_interested_for',
        'branch',
        'follow_up_by_display',
        'next_followup_reminder',
        'created_at',
    )
    list_display_links = ('id', 'name', 'mobile_number')

    list_filter = (
        'status',
        'priority',
        'branch',
        'source',
        'call_response',
        'student_interested_for',
        'created_at',
        'follow_up_date',
        'next_followup_reminder',
    )

    search_fields = (
        'name',
        'mobile_number',
        'address',
        'follow_up_notes',
    )

    list_per_page = 50
    ordering = ('-id',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Student Information', {
            'fields': (
                'name',
                'mobile_number',
                'student_interested_for',
                'source',
                'address',
            )
        }),
        ('Lead Status & Branch', {
            'fields': (
                'status',
                'priority',
                'branch',
            )
        }),
        ('Follow-up Details', {
            'fields': (
                'follow_up_by',
                'call_response',
                'follow_up_date',
                'next_followup_reminder',
                'follow_up_notes',
            )
        }),
        ('Class Information', {
            'fields': (
                'class_start_date',
            ),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': (
                'created_at',
            ),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at',)

    def status_badge(self, obj):
        if not obj.status:
            return mark_safe('<span class="badge" style="background:#6c757d; color:#fff; padding:3px 8px; border-radius:10px;">Not Set</span>')

        status_colors = {
            'interested': '#0d6efd',
            'planning': '#6610f2',
            'under_review': '#fd7e14',
            'on_hold': '#f59e0b',
            'trader': '#0284c7',
            'class_joined': '#198754',
            'class_completed': '#20c997',
            'not_interested': '#dc3545',
        }
        color = status_colors.get(obj.status, '#6c757d')
        text_color = '#000' if obj.status in ['on_hold'] else '#fff'
        return format_html(
            '<span class="badge" style="background:{}; color:{}; padding:4px 10px; border-radius:12px; font-weight:600; font-size:11px;">{}</span>',
            color,
            text_color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def priority_badge(self, obj):
        if not obj.priority:
            return mark_safe('<span class="badge" style="background:#6c757d; color:#fff; padding:3px 8px; border-radius:10px;">Not Set</span>')

        priority_colors = {
            'high': '#dc3545',
            'medium': '#fd7e14',
            'low': '#6c757d',
        }
        color = priority_colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span class="badge" style="background:{}; color:#fff; padding:4px 8px; border-radius:10px; font-weight:600; font-size:11px;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'

    def follow_up_by_display(self, obj):
        if obj.follow_up_by:
            return obj.follow_up_by.name or obj.follow_up_by.mobile_number or str(obj.follow_up_by)
        return mark_safe('<span style="color:#9ca3af;">—</span>')
    follow_up_by_display.short_description = 'Follow-up By'

    # ================== Bulk Actions ==================
    actions = ['delete_selected_followups', 'delete_all_followups_action', 'mark_as_completed', 'mark_as_not_interested']

    def delete_selected_followups(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"Successfully deleted {count} selected follow-up record(s) in bulk.", messages.SUCCESS)
    delete_selected_followups.short_description = "Delete selected follow-up records (Bulk)"

    def delete_all_followups_action(self, request, queryset):
        if not request.user.is_superuser:
            self.message_user(request, "Only superusers are authorized to delete all records.", messages.ERROR)
            return HttpResponseRedirect(request.get_full_path())
        return HttpResponseRedirect(reverse('admin:crmfollowup_delete_all'))
    delete_all_followups_action.short_description = "⚠️ Delete ALL Follow-up Records (Bulk Wipe)"

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='class_completed')
        self.message_user(request, f"{updated} follow-up(s) marked as Class Completed.")
    mark_as_completed.short_description = "Mark selected as Class Completed"

    def mark_as_not_interested(self, request, queryset):
        updated = queryset.update(status='not_interested')
        self.message_user(request, f"{updated} follow-up(s) marked as Not Interested.")
    mark_as_not_interested.short_description = "Mark selected as Not Interested"

    # ================== Custom URLs for Delete All ==================
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('delete-all/', self.admin_site.admin_view(self.delete_all_view), name='crmfollowup_delete_all'),
        ]
        return custom_urls + urls

    def delete_all_view(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers are authorized to bulk delete all records.")

        total_count = CRMFollowup.objects.count()

        if request.method == 'POST':
            deleted_count, _ = CRMFollowup.objects.all().delete()
            self.message_user(request, f"Successfully deleted all {total_count} follow-up record(s) in bulk.", messages.SUCCESS)
            return HttpResponseRedirect(reverse('admin:AdminApp_crmfollowup_changelist'))

        context = {
            **self.admin_site.each_context(request),
            'title': 'Delete All CRM Follow-up Records',
            'total_count': total_count,
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/AdminApp/crmfollowup/delete_all_confirmation.html', context)
