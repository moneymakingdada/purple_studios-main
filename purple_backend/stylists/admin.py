from django.contrib import admin

from .models import Availability, PortfolioImage, StylistProfile, TimeOff


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1


class TimeOffInline(admin.TabularInline):
    model = TimeOff
    extra = 0


class PortfolioInline(admin.TabularInline):
    model = PortfolioImage
    extra = 0


@admin.register(StylistProfile)
class StylistProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "salon", "years_experience", "is_accepting_bookings", "average_rating")
    list_filter = ("salon", "is_accepting_bookings")
    search_fields = ("user__first_name", "user__last_name", "user__email", "title")
    filter_horizontal = ("specialties",)
    inlines = [AvailabilityInline, TimeOffInline, PortfolioInline]
