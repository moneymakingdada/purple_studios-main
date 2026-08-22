import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from salons.models import Salon
from services.models import Service
from stylists.models import StylistProfile


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No show"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings"
    )
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name="bookings")
    stylist = models.ForeignKey(StylistProfile, on_delete=models.CASCADE, related_name="bookings")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="bookings")

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    price = models.DecimalField(max_digits=8, decimal_places=2, help_text="Snapshot of service price in GHS")
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-start_time"]
        indexes = [models.Index(fields=["stylist", "date"])]

    def __str__(self):
        return f"{self.customer} → {self.stylist} · {self.service} on {self.date} {self.start_time}"

    def clean(self):
        overlapping = Booking.objects.filter(
            stylist=self.stylist,
            date=self.date,
            status__in=[self.Status.PENDING, self.Status.CONFIRMED],
        ).exclude(pk=self.pk)
        for booking in overlapping:
            if self.start_time < booking.end_time and self.end_time > booking.start_time:
                raise ValidationError("This stylist already has a booking that overlaps this time slot.")

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.service.price
        self.full_clean()
        super().save(*args, **kwargs)


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="review")
    rating = models.PositiveSmallIntegerField(help_text="1-5")
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not (1 <= self.rating <= 5):
            raise ValidationError("Rating must be between 1 and 5.")
        if self.booking.status != Booking.Status.COMPLETED:
            raise ValidationError("You can only review a completed booking.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.rating}★ for {self.booking}"
