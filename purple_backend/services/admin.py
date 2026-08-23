from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Service, ServiceCategory


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0
    fields = ("name", "audience", "duration_minutes", "price", "is_active")


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(ModelAdmin):
    list_display = ("name", "order")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ServiceInline]


@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    list_display = ("name", "category", "audience", "duration_minutes", "price", "is_active")
    list_filter = ("category", "audience", "is_active")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
