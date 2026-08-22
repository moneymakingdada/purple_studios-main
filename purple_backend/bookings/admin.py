from django.contrib import admin

from .models import Booking, Review


class ReviewInline(admin.StackedInline):
    model = Review
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "stylist", "service", "salon", "date", "start_time", "status", "price")
    list_filter = ("status", "salon", "date")
    search_fields = ("customer__email", "customer__first_name", "customer__last_name", "stylist__user__email")
    date_hierarchy = "date"
    inlines = [ReviewInline]
    actions = ["mark_confirmed", "mark_completed", "mark_cancelled"]

    @admin.action(description="Mark selected bookings as confirmed")
    def mark_confirmed(self, request, queryset):
        queryset.update(status=Booking.Status.CONFIRMED)

    @admin.action(description="Mark selected bookings as completed")
    def mark_completed(self, request, queryset):
        queryset.update(status=Booking.Status.COMPLETED)

    @admin.action(description="Mark selected bookings as cancelled")
    def mark_cancelled(self, request, queryset):
        queryset.update(status=Booking.Status.CANCELLED)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("booking", "rating", "created_at")
    list_filter = ("rating",)
