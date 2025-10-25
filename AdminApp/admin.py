from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from .models import PhotoGalleryCategories, PhotoGallery, VideoGallery

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
