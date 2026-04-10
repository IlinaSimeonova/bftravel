from django.contrib import admin
from django.utils.html import format_html

from .models import BookedTrip, VisitedPlace


@admin.register(BookedTrip)
class BookedTripAdmin(admin.ModelAdmin):
    list_display = ['destination', 'start_date', 'end_date', 'has_photo', 'has_coordinates']
    list_filter = ['start_date']
    search_fields = ['destination']
    ordering = ['-start_date']

    fieldsets = (
        ('Trip Info', {
            'fields': ('destination', 'start_date', 'end_date')
        }),
        ('Map Display (for after trip ends)', {
            'fields': ('latitude', 'longitude', 'photo', 'notes'),
            'description': 'Add coordinates and a photo to show this trip on the map after it ends.'
        }),
    )

    def has_photo(self, obj):
        return bool(obj.photo)
    has_photo.boolean = True
    has_photo.short_description = 'Photo'

    def has_coordinates(self, obj):
        return bool(obj.latitude and obj.longitude)
    has_coordinates.boolean = True
    has_coordinates.short_description = 'On Map'


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
