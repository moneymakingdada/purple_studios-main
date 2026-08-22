import uuid

from django.db import models


class ServiceCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon name for frontend, e.g. 'scissors'")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Service categories"

    def __str__(self):
        return self.name


class Service(models.Model):
    class Audience(models.TextChoices):
        MEN = "men", "Men"
        WOMEN = "women", "Women"
        UNISEX = "unisex", "Unisex"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    audience = models.CharField(max_length=10, choices=Audience.choices, default=Audience.UNISEX)
    duration_minutes = models.PositiveIntegerField(default=60)
    price = models.DecimalField(max_digits=8, decimal_places=2, help_text="Price in GHS")
    image = models.ImageField(upload_to="services/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category__order", "name"]

    def __str__(self):
        return f"{self.name} (GHS {self.price})"
