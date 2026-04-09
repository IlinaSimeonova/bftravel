from django.contrib import admin
from django.utils.html import format_html
from .models import VisitedPlace


@admin.register(VisitedPlace)
class VisitedPlaceAdmin(admin.ModelAdmin):
    list_display = ['display_location', 'date_visited', 'photo_preview', 'created_at']
    list_filter = ['country', 'date_visited']
    search_fields = ['country', 'city', 'notes']
    ordering = ['-date_visited']

    fieldsets = (
        ('Location', {
            'fields': ('country', 'city', 'latitude', 'longitude')
        }),
        ('Trip Details', {
            'fields': ('date_visited', 'photo', 'notes')
        }),
    )

    def photo_preview(self, obj):
        """Show small preview of the photo in admin list."""
        if obj.photo:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.photo.url
            )
        return '-'
    photo_preview.short_description = 'Photo'
