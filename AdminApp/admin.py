from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from .models import PhotoGalleryCategories, PhotoGallery, VideoGallery, CustomUser, FreeCourse, FreeCourseProgress, Enquiry,EventRegistration,Event,Basic_to_Advance_Cource,Advance_to_Pro_Cource,Certificate



from django.contrib import admin
from .models import Enquiry
from django.utils.html import format_html
from django.utils.timezone import localtime


# -----------------------------
# Enquiry ADMIN
# ----------------------------- 
@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    # 🧩 List view customization
    list_display = (
        'id',
        'full_name',
        'phone',
        'email_link',
        'short_message',
        'submitted_time',
        'remark_status',
    )
    list_display_links = ('id', 'full_name')
    list_per_page = 20
    ordering = ('-submitted_at',)
    search_fields = ('full_name', 'email', 'phone', 'message')
    list_filter = ('submitted_at',)

    # 🧠 Field organization
    fieldsets = (
        ('🧍 Enquiry Details', {
            'fields': ('full_name', 'phone', 'email')
        }),
        ('💬 Message', {
            'fields': ('message',)
        }),
        ('🕓 Admin Use Only', {
            'classes': ('collapse',),
            'fields': ('remark',)
        }),
    )

    # 🪶 Read-only fields
    readonly_fields = ('submitted_at',)

    # 🎨 Custom admin UI tweaks
    def email_link(self, obj):
        """Clickable email link"""
        return format_html('<a href="mailto:{}">{}</a>', obj.email, obj.email)
    email_link.short_description = "Email"

    def short_message(self, obj):
        """Short preview of message"""
        return (obj.message[:50] + '...') if len(obj.message) > 50 else obj.message
    short_message.short_description = "Message Preview"

    def submitted_time(self, obj):
        """Formatted datetime"""
        return localtime(obj.submitted_at).strftime('%d %b %Y, %I:%M %p')
    submitted_time.short_description = "Submitted On"

    def remark_status(self, obj):
        """Status badge for remark"""
        if obj.remark:
            return format_html('<span style="color: green; font-weight: bold;">✔ Remark Added</span>')
        return format_html('<span style="color: gray;">— Pending —</span>')
    remark_status.short_description = "Remark Status"

    # 💡 Advanced features
    actions = ['mark_as_reviewed', 'export_selected_to_csv']

    def mark_as_reviewed(self, request, queryset):
        """Mark enquiries as reviewed"""
        count = queryset.update(remark='Reviewed')
        self.message_user(request, f'{count} enquiries marked as reviewed.')
    mark_as_reviewed.short_description = "✅ Mark selected enquiries as reviewed"

    def export_selected_to_csv(self, request, queryset):
        """Export enquiries to CSV"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="enquiries.csv"'

        writer = csv.writer(response)
        writer.writerow(['Full Name', 'Phone', 'Email', 'Message', 'Submitted At', 'Remark'])
        for obj in queryset:
            writer.writerow([
                obj.full_name,
                obj.phone,
                obj.email,
                obj.message,
                obj.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
                obj.remark or ''
            ])
        return response
    export_selected_to_csv.short_description = "⬇️ Export selected enquiries to CSV"







# -----------------------------
# Custome user 
# -----------------------------
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.timezone import localtime
from .models import CustomUser

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.timezone import localtime
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.shortcuts import redirect
from django.urls import path
from django.template.response import TemplateResponse
from django.contrib import messages
from .models import CustomUser



# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     change_password_form = AdminPasswordChangeForm

#     list_display = (
#         'id',
#         'name',
#         'mobile_number',
#         'email_link',
#         'location_info',
#         'dob_display',
#         'role',
#         'is_active_colored',
#         'is_active',
#         'date_joined_display',
#     )

#     list_display_links = ('id', 'name')
#     ordering = ('-date_joined',)
#     list_per_page = 20
#     search_fields = ('name', 'mobile_number', 'email', 'dist', 'village', 'taluka')
#     list_filter = ('role', 'is_active', 'dist', 'taluka', 'village', 'date_joined')
#     list_editable = ('is_active',)
#     readonly_fields = ('last_login', 'date_joined')

#     fieldsets = (
#         ('👤 Personal Information', {
#             'fields': ('name', 'dob', 'mobile_number', 'email', 'password')
#         }),
#         ('🏡 Location Details', {
#             'fields': ('dist', 'taluka', 'village'),
#         }),
#         ('📝 Additional Info', {
#             'fields': ('action',),
#         }),
#         ('🔒 Permissions & Status', {
#             'fields': ('role', 'is_active', 'is_staff'),
#         }),
#         ('📅 Important Dates', {
#             'classes': ('collapse',),
#             'fields': ('last_login', 'date_joined'),
#         }),
#     )

#     add_fieldsets = (
#         ('👤 Basic Info', {
#             'classes': ('wide',),
#             'fields': (
#                 'mobile_number',
#                 'name',
#                 'email',
#                 'password1',
#                 'password2',
#                 'role',
#                 'dist',
#                 'taluka',
#                 'village',
#                 'dob',
#                 'action',
#                 'is_active',
#                 'is_staff'
#             ),
#         }),
#     )

    # def email_link(self, obj):
    #     if obj.email:
    #         return format_html('<a href="mailto:{}">{}</a>', obj.email, obj.email)
    #     return format_html('<span style="color:gray;">—</span>')
    # email_link.short_description = "Email"

    # def location_info(self, obj):
    #     if obj.village or obj.taluka or obj.dist:
    #         return f"{obj.village}, {obj.taluka}, {obj.dist}"
    #     return "—"
    # location_info.short_description = "Location"

    # def dob_display(self, obj):
    #     return obj.dob.strftime('%d %b %Y') if obj.dob else "—"
    # dob_display.short_description = "DOB"

    # def date_joined_display(self, obj):
    #     return localtime(obj.date_joined).strftime('%d %b %Y, %I:%M %p')
    # date_joined_display.short_description = "Joined On"

    # def is_active_colored(self, obj):
    #     color = "green" if obj.is_active else "red"
    #     text = "🟢 Active" if obj.is_active else "🔴 Inactive"
    #     return format_html(
    #         '<span style="color:{}; font-weight:bold;">{}</span>',
    #         color,
    #         text
    #     )
    # is_active_colored.short_description = "Status"
    # is_active_colored.admin_order_field = 'is_active'

    # actions = ['activate_users', 'deactivate_users', 'export_selected_users']

    # def activate_users(self, request, queryset):
    #     count = queryset.update(is_active=True)
    #     self.message_user(request, f"{count} user(s) activated successfully.")
    # activate_users.short_description = "✅ Activate selected users"

    # def deactivate_users(self, request, queryset):
    #     count = queryset.update(is_active=False)
    #     self.message_user(request, f"{count} user(s) deactivated successfully.")
    # deactivate_users.short_description = "🚫 Deactivate selected users"

    # def export_selected_users(self, request, queryset):
    #     import csv
    #     from django.http import HttpResponse

    #     response = HttpResponse(content_type='text/csv')
    #     response['Content-Disposition'] = 'attachment; filename="users.csv"'

    #     writer = csv.writer(response)
    #     writer.writerow([
    #         'Name', 'Mobile', 'Email', 'Role', 'District',
    #         'Taluka', 'Village', 'DOB', 'Action',
    #         'Active', 'Date Joined'
    #     ])

    #     for obj in queryset:
    #         writer.writerow([
    #             obj.name,
    #             obj.mobile_number,
    #             obj.email or '',
    #             obj.get_role_display(),
    #             obj.dist,
    #             obj.taluka,
    #             obj.village,
    #             obj.dob.strftime('%Y-%m-%d') if obj.dob else '',
    #             obj.action or '',
    #             'Yes' if obj.is_active else 'No',
    #             obj.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
    #         ])
    #     return response
    # export_selected_users.short_description = "⬇️ Export selected users to CSV"

    # def get_urls(self):
    #     urls = super().get_urls()
    #     custom_urls = [
    #         path(
    #             '<id>/change-password/',
    #             self.admin_site.admin_view(self.change_user_password),
    #             name='customuser_change_password',
    #         ),
    #     ]
    #     return custom_urls + urls

    # def change_user_password(self, request, id, form_url=''):
    #     user = self.get_object(request, id)
    #     if not user:
    #         messages.error(request, "User not found.")
    #         return redirect('..')

    #     if request.method == 'POST':
    #         form = self.change_password_form(user, request.POST)
    #         if form.is_valid():
    #             form.save()
    #             messages.success(
    #                 request,
    #                 f"Password for {user.name or user.mobile_number} changed successfully!"
    #             )
    #             return redirect('..')
    #     else:
    #         form = self.change_password_form(user)

    #     context = {
    #         **self.admin_site.each_context(request),
    #         'title': f'Change password: {user.name or user.mobile_number}',
    #         'form': form,
    #         'opts': self.model._meta,
    #         'original': user,
    #     }
    #     return TemplateResponse(
    #         request,
    #         'admin/auth/user/change_password.html',
    #         context
    #     )
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
# Inline for FreeCourseProgress
# ----------------------------
class FreeCourseProgressInline(admin.TabularInline):
    model = FreeCourseProgress
    extra = 0
    readonly_fields = ('student', 'watched_duration', 'completed', 'completed_at', 'certificate_ready_display')
    can_delete = False
    verbose_name = "Student Progress"
    verbose_name_plural = "Students Progress"

    def certificate_ready_display(self, obj):
        if obj.certificate_ready:
            return format_html('<span style="color:green;">✔ Ready</span>')
        return format_html('<span style="color:red;">✖ Not Ready</span>')
    certificate_ready_display.short_description = "Certificate Status"

# ----------------------------
# FreeCourse Admin
# ----------------------------
@admin.register(FreeCourse)
class FreeCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'video_file_link', 'certificate_file_link')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)
    inlines = [FreeCourseProgressInline]
    list_filter = ('created_at',)

    # Show video file as clickable link
    def video_file_link(self, obj):
        if obj.video:
            return format_html('<a href="{}" target="_blank">View Video</a>', obj.video.url)
        return "-"
    video_file_link.short_description = "Video"

    # Show certificate file as clickable link
    def certificate_file_link(self, obj):
        if obj.certificate_template:
            return format_html('<a href="{}" target="_blank">View Certificate</a>', obj.certificate_template.url)
        return "-"
    certificate_file_link.short_description = "Certificate"

# ----------------------------
# FreeCourseProgress Admin
# ----------------------------
@admin.register(FreeCourseProgress)
class FreeCourseProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'watched_duration', 'completed', 'completed_at', 'certificate_ready_display')
    list_filter = ('completed', 'course')
    search_fields = ('student__name', 'course__title')
    readonly_fields = ('watched_duration', 'completed_at', 'certificate_ready_display')
    actions = ['mark_completed_action']

    def certificate_ready_display(self, obj):
        if obj.certificate_ready:
            return format_html('<span style="color:green;">✔ Ready</span>')
        return format_html('<span style="color:red;">✖ Not Ready</span>')
    certificate_ready_display.short_description = "Certificate Status"

    # Admin action to mark selected progress as completed
    def mark_completed_action(self, request, queryset):
        updated = 0
        for progress in queryset:
            if not progress.completed:
                progress.mark_completed()
                updated += 1
        self.message_user(request, f"{updated} progress records marked as completed.")
    mark_completed_action.short_description = "Mark selected as Completed"





from django.contrib import admin
from django.utils.html import format_html
from .models import Basic_to_Advance_Cource, Advance_to_Pro_Cource


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
    readonly_fields = ('thumbnail_preview',)
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
            'fields': ('thumbnail', 'thumbnail_preview')
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
        return format_html('<span style="color:gray;">No Image</span>')
    thumbnail_preview.short_description = "Thumbnail"

    def get_queryset(self, request):
        """Enhance query performance."""
        return super().get_queryset(request).only(
            'title', 'event_date', 'time', 'duration', 'rating',
            'total_reviews', 'offer_price', 'original_price', 'thumbnail', 'is_active'
        )


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







@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'registration_id',
        'full_name',
        'email',
        'event',
        'amount_paid',
        'payment_status',
        'created_at',
    )

    list_filter = (
        'payment_status',
        'event',
        'created_at',
    )

    search_fields = (
        'registration_id',
        'full_name',
        'email',
        'mobile_number',
        'event__title',
    )

    readonly_fields = (
        'registration_id',
        'razorpay_order_id',
        'razorpay_payment_id',
        'razorpay_signature',
        'created_at',
        'updated_at',
    )

    ordering = ('-created_at',)
    list_per_page = 25

    fieldsets = (
        ('Registration Details', {
            'fields': ('registration_id', 'event', 'payment_status'),
            'classes': ('wide',)
        }),
        ('Personal Information', {
            'fields': ('full_name', 'email', 'mobile_number', 'address'),
            'classes': ('collapse',)
        }),
        ('Payment Information', {
            'fields': (
                'amount_paid',
                'razorpay_order_id',
                'razorpay_payment_id',
                'razorpay_signature',
            ),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('special_requirements',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Optional Jazzmin customization
    jazzmin_icon = "fa fa-ticket"  # You can pick any FontAwesome icon

    def get_queryset(self, request):
        """Optimize queryset by selecting related event"""
        qs = super().get_queryset(request)
        return qs.select_related('event')
    

 
from .models import CRM_Student_Interested_for_options, CRMFollowup

# Register your models here.

class CRM_Student_Interested_for_optionsAdmin(admin.ModelAdmin):
    list_display = ('interest_option',)
    search_fields = ('interest_option',)
    ordering = ('interest_option',)
    
    # Simple configuration since this is just a lookup table
    list_per_page = 20

admin.site.register(CRM_Student_Interested_for_options, CRM_Student_Interested_for_optionsAdmin)


class CRMFollowupAdmin(admin.ModelAdmin):
    # ================== Display Configuration ==================
    list_display = (
        'name', 
        'mobile_number', 
        'status_badge', 
        'priority_badge', 
        'follow_up_by_display',
        'next_followup_reminder',
        'student_interested_for',
        'source'
    )
    
    list_display_links = ('name', 'mobile_number')
    
    # ================== Filters & Search ==================
    list_filter = (
        'status',
        'priority',
        'source',
        'call_response',
        'student_interested_for',
        'follow_up_by',
        'follow_up_date',
    )
    
    search_fields = (
        'name',
        'mobile_number',
        'follow_up_notes',
    )
    
    # ================== Layout & Ordering ==================
    list_per_page = 25
    ordering = ('-follow_up_date', '-created_at')
    date_hierarchy = 'follow_up_date'
    
    # ================== Custom Fieldsets for Form View ==================
    fieldsets = (
        ('Student Information', {
            'fields': (
                'name',
                'mobile_number',
                'student_interested_for',
                'source'
            ),
            'classes': ('collapse',)
        }),
        ('Lead Status', {
            'fields': (
                'status',
                'priority',
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
    
    # ================== Readonly Fields ==================
    readonly_fields = ('created_at',)
    
    # ================== Custom Methods for Display ==================
    def status_badge(self, obj):
        if not obj.status:
            return format_html('<span class="badge badge-secondary">Not Set</span>')
        
        status_colors = {
            'interested': 'info',
            'planning': 'primary',
            'under_review': 'warning',
            'on_hold': 'secondary',
            'class_joined': 'success',
            'class_completed': 'success',
            'not_interested': 'danger',
        }
        color = status_colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def priority_badge(self, obj):
        if not obj.priority:
            return format_html('<span class="badge badge-secondary">Not Set</span>')
        
        priority_colors = {
            'high': 'danger',
            'medium': 'warning',
            'low': 'info',
        }
        color = priority_colors.get(obj.priority, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def follow_up_by_display(self, obj):
        if obj.follow_up_by:
            if hasattr(obj.follow_up_by, 'get_full_name') and obj.follow_up_by.get_full_name():
                return obj.follow_up_by.get_full_name()
            return str(obj.follow_up_by)
        return "Not Assigned"
    follow_up_by_display.short_description = 'Follow-up By'
    
    # ================== Action Configuration ==================
    actions = ['mark_as_high_priority', 'mark_as_completed', 'mark_as_not_interested']
    
    def mark_as_high_priority(self, request, queryset):
        updated = queryset.update(priority='high')
        self.message_user(request, f'{updated} follow-up(s) marked as High Priority.')
    mark_as_high_priority.short_description = "Mark selected as High Priority"
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='class_completed')
        self.message_user(request, f'{updated} follow-up(s) marked as Class Completed.')
    mark_as_completed.short_description = "Mark selected as Class Completed"
    
    def mark_as_not_interested(self, request, queryset):
        updated = queryset.update(status='not_interested')
        self.message_user(request, f'{updated} follow-up(s) marked as Not Interested.')
    mark_as_not_interested.short_description = "Mark selected as Not Interested"
    
    # ================== Form Customization ==================
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make some fields not required in admin if needed
        return form
    
    # ================== Save Method Customization ==================
    def save_model(self, request, obj, form, change):
        # You can add custom save logic here
        super().save_model(request, obj, form, change)
    
    # ================== Change List View Customization ==================
    def changelist_view(self, request, extra_context=None):
        # Add custom context if needed
        extra_context = extra_context or {}
        extra_context['title'] = 'CRM Follow-ups Management'
        return super().changelist_view(request, extra_context=extra_context)


from .models import  Branch
 

# Register the Branch model
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch_name')  # Customize which fields are displayed in the list view
    search_fields = ('branch_name',)  # Add search functionality for the 'branch_name'
    list_filter = ('branch_name',)  # Add filter options for the 'branch_name' field
    ordering = ('id',)  # Sort by 'id' by default
    fieldsets = (
        (None, {
            'fields': ('branch_name',)  # Define fields to display on the model detail page
        }),
    )



admin.site.register(CRMFollowup, CRMFollowupAdmin)
admin.site.register(Branch, BranchAdmin)



# admin.py

# # Register your models with the customized admin interfaces
# admin.site.register(CRM_Student_Interested_for_options)
