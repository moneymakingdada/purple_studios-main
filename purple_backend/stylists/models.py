import uuid

from django.conf import settings
from django.db import models

from salons.models import Salon
from services.models import Service

WEEKDAYS = [
    (0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"),
    (4, "Friday"), (5, "Saturday"), (6, "Sunday"),
]


class StylistProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stylist_profile")
    salon = models.ForeignKey(Salon, on_delete=models.SET_NULL, null=True, related_name="stylists")
    title = models.CharField(max_length=120, help_text="e.g. Senior colour & cut specialist")
    bio = models.TextField(blank=True)
    specialties = models.ManyToManyField(Service, blank=True, related_name="stylists")
    years_experience = models.PositiveIntegerField(default=0)
    is_accepting_bookings = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def average_rating(self):
        from bookings.models import Review
        agg = Review.objects.filter(booking__stylist=self).aggregate(models.Avg("rating"))
        return round(agg["rating__avg"] or 0, 2)


class Availability(models.Model):
    """Recurring weekly availability window for a stylist."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stylist = models.ForeignKey(StylistProfile, on_delete=models.CASCADE, related_name="availability")
    weekday = models.IntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["weekday", "start_time"]
        verbose_name_plural = "Availability"
        unique_together = ("stylist", "weekday", "start_time")

    def __str__(self):
        return f"{self.stylist} — {self.get_weekday_display()} {self.start_time}-{self.end_time}"


class TimeOff(models.Model):
    """One-off blocked dates (holiday, sick day) that override availability."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stylist = models.ForeignKey(StylistProfile, on_delete=models.CASCADE, related_name="time_off")
    date = models.DateField()
    reason = models.CharField(max_length=120, blank=True)

    class Meta:
        unique_together = ("stylist", "date")

    def __str__(self):
        return f"{self.stylist} off on {self.date}"


class PortfolioImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stylist = models.ForeignKey(StylistProfile, on_delete=models.CASCADE, related_name="portfolio")
    image = models.ImageField(upload_to="portfolio/")
    caption = models.CharField(max_length=140, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.stylist} portfolio #{self.order}"
