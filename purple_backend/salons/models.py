import uuid

from django.db import models

GHANA_REGIONS = [
    ("greater_accra", "Greater Accra"),
    ("ashanti", "Ashanti"),
    ("western", "Western"),
    ("eastern", "Eastern"),
    ("central", "Central"),
    ("volta", "Volta"),
    ("northern", "Northern"),
    ("bono", "Bono"),
]


class Salon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    city = models.CharField(max_length=80, help_text="e.g. Accra, Kumasi, Takoradi")
    region = models.CharField(max_length=30, choices=GHANA_REGIONS, default="greater_accra")
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=13, blank=True)
    opens_at = models.TimeField(default="09:00")
    closes_at = models.TimeField(default="19:00")
    cover_image = models.ImageField(upload_to="salons/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} — {self.city}"
