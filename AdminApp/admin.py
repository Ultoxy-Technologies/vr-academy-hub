from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from .models import PhotoGalleryCategories, PhotoGallery, VideoGallery



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


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # 🧩 List view configuration
    list_display = (
        'id',
        'name',
        'mobile_number',
        'email_link',
        'location_info',
        'dob_display',
        'is_active_colored',   # Styled column
        'is_active',           # Actual field (for list_editable)
        'date_joined_display',
    )
    list_display_links = ('id', 'name')
    ordering = ('-date_joined',)
    list_per_page = 20
    search_fields = ('name', 'mobile_number', 'email', 'dist', 'village')
    list_filter = ('is_active', 'dist', 'taluka', 'village', 'date_joined')

    # ✅ Allow inline editing of is_active
    list_editable = ('is_active',)

    # 🧠 Field organization
    fieldsets = (
        ('👤 Personal Information', {
            'fields': ('username', 'name', 'dob', 'mobile_number', 'email')
        }),
        ('🏡 Location Details', {
            'fields': ('dist', 'taluka', 'village'),
        }),
        ('🔒 Permissions & Status', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('📅 Important Dates', {
            'classes': ('collapse',),
            'fields': ('last_login', 'date_joined'),
        }),
    )

    # 🧾 Fields for adding a new user
    add_fieldsets = (
        ('👤 Basic Info', {
            'classes': ('wide',),
            'fields': ('mobile_number', 'name', 'email', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

    readonly_fields = ('last_login', 'date_joined')

    # 🎨 Custom display functions
    def email_link(self, obj):
        """Clickable email link"""
        if obj.email:
            return format_html('<a href="mailto:{}">{}</a>', obj.email, obj.email)
        return format_html('<span style="color:gray;">—</span>')
    email_link.short_description = "Email"

    def location_info(self, obj):
        """Concise location summary"""
        return f"{obj.village}, {obj.taluka}, {obj.dist}"
    location_info.short_description = "Location"

    def dob_display(self, obj):
        """Show formatted DOB"""
        return obj.dob.strftime('%d %b %Y') if obj.dob else "—"
    dob_display.short_description = "DOB"

    def date_joined_display(self, obj):
        """Show formatted join date"""
        return localtime(obj.date_joined).strftime('%d %b %Y, %I:%M %p')
    date_joined_display.short_description = "Joined On"

    def is_active_colored(self, obj):
        """Color-coded status"""
        color = "green" if obj.is_active else "red"
        text = "🟢 Active" if obj.is_active else "🔴 Inactive"
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, text)
    is_active_colored.short_description = "Status"
    is_active_colored.admin_order_field = 'is_active'

    # 💡 Custom actions
    actions = ['activate_users', 'deactivate_users', 'export_selected_users']

    def activate_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} user(s) activated successfully.")
    activate_users.short_description = "✅ Activate selected users"

    def deactivate_users(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} user(s) deactivated successfully.")
    deactivate_users.short_description = "🚫 Deactivate selected users"

    def export_selected_users(self, request, queryset):
        """Export selected users to CSV"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Name', 'Mobile', 'Email', 'District',
            'Taluka', 'Village', 'DOB', 'Active', 'Date Joined'
        ])
        for obj in queryset:
            writer.writerow([
                obj.name,
                obj.mobile_number,
                obj.email or '',
                obj.dist,
                obj.taluka,
                obj.village,
                obj.dob.strftime('%Y-%m-%d') if obj.dob else '',
                'Yes' if obj.is_active else 'No',
                obj.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        return response
    export_selected_users.short_description = "⬇️ Export selected users to CSV"


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


@admin.register(VideoGallery)
class VideoGalleryAdmin(admin.ModelAdmin):
    list_display = ('caption', 'video_link', 'video_preview')
    search_fields = ('caption', 'video_link')
    list_per_page = 20

    # Keep preview visible but not interfering with editing
    readonly_fields = ('preview_display',)

    fieldsets = (
        ('Video Details', {
            'fields': ('caption', 'video_link')
        }),
        ('Preview', {
            'fields': ('preview_display',),
            'description': 'Live preview of your YouTube video below after saving or updating the link.'
        }),
    )

    def preview_display(self, obj):
        """Show an embedded YouTube preview if the link is valid."""
        if not obj.video_link:
            return "No video link provided."

        video_id = self.extract_youtube_id(obj.video_link)
        if video_id:
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            return format_html(
                '<iframe width="360" height="200" src="{}" frameborder="0" '
                'allowfullscreen style="border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.2);"></iframe>',
                embed_url
            )
        return "Invalid or unsupported YouTube link."
    preview_display.short_description = "Video Preview"

    def extract_youtube_id(self, url):
        """Extracts YouTube video ID from various URL formats."""
        regex_patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:\?|&|$)',  # normal or embedded YouTube URL
            r'youtu\.be\/([0-9A-Za-z_-]{11})'           # shortened YouTube link
        ]
        for pattern in regex_patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def video_preview(self, obj):
        """For list_display column preview (small version)."""
        video_id = self.extract_youtube_id(obj.video_link or "")
        if video_id:
            return format_html(
                '<iframe width="180" height="100" src="https://www.youtube.com/embed/{}" '
                'frameborder="0" allowfullscreen></iframe>', video_id
            )
        return "—"
    video_preview.short_description = "Preview"
