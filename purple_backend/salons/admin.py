from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Salon


@admin.register(Salon)
class SalonAdmin(ModelAdmin):
    list_display = ("name", "city", "region", "phone", "opens_at", "closes_at", "is_active")
    list_filter = ("region", "is_active")
    search_fields = ("name", "city", "address")
    prepopulated_fields = {"slug": ("name",)}
