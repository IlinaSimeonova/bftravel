from django.db import models


class Destination(models.Model):
    """
    Cached destination info from Claude API.
    Once fetched, info is stored here and reused.
    """
    name = models.CharField(max_length=200, unique=True, help_text="Destination name")

    # Cached travel info (JSON)
    best_time = models.JSONField(default=dict)
    travel_tips = models.JSONField(default=dict)
    visa = models.JSONField(default=dict)
    health = models.JSONField(default=dict)
    must_sees = models.JSONField(default=dict)
    food = models.JSONField(default=dict)
    budget = models.JSONField(default=dict)

    # Photo - optional, users can upload their own
    photo = models.ImageField(upload_to='destinations/', blank=True, null=True)

    # Static image filename (for pre-seeded destinations)
    image_filename = models.CharField(max_length=100, blank=True, help_text="Filename in static/images/")

    # Is this a "dream list" destination (shows on main list)
    is_dream_destination = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_dream_destination', 'name']

    def __str__(self):
        return self.name


class BookedTrip(models.Model):
    """
    Represents a trip that Dessi & Martin have booked.
    Shows on the landing page as upcoming/current/past adventure.
    """
    destination = models.CharField(max_length=200, help_text="Destination name (e.g., Japan, Thailand)")
    start_date = models.DateField(help_text="Trip start date")
    end_date = models.DateField(help_text="Trip end date")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Booked Trip"
        verbose_name_plural = "Booked Trips"

    def __str__(self):
        return f"{self.destination} ({self.start_date} - {self.end_date})"


class WoodyChat(models.Model):
    """
    Stores chat history with Woody AI assistant per destination.
    """
    destination = models.CharField(max_length=200, help_text="Destination being discussed")
    role = models.CharField(max_length=20, help_text="user or assistant")
    content = models.TextField(help_text="Message content")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.destination} - {self.role}: {self.content[:50]}"


class VisitedPlace(models.Model):
    """
    Represents a place (country/city) that Dessi & Martin have visited.
    Each place will appear on the interactive map.
    """
    country = models.CharField(max_length=100, help_text="Country name (e.g., Thailand, Japan)")
    city = models.CharField(max_length=100, blank=True, help_text="City name (optional)")

    # Geographic coordinates for map marker
    latitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="Latitude coordinate")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="Longitude coordinate")

    # Trip details
    date_visited = models.DateField(help_text="When they visited (or start date of trip)")
    photo = models.ImageField(upload_to='travel_photos/', help_text="Photo from this place")
    notes = models.TextField(blank=True, help_text="Optional notes about the visit")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_visited']
        verbose_name = "Visited Place"
        verbose_name_plural = "Visited Places"

    def __str__(self):
        if self.city:
            return f"{self.city}, {self.country} ({self.date_visited.year})"
        return f"{self.country} ({self.date_visited.year})"

    @property
    def display_location(self):
        """Returns formatted location string for display."""
        if self.city:
            return f"{self.city}, {self.country}"
        return self.country
