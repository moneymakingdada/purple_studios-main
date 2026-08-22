from rest_framework import serializers

from services.serializers import ServiceSerializer

from .models import Availability, PortfolioImage, StylistProfile, TimeOff


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ("id", "weekday", "start_time", "end_time")


class TimeOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeOff
        fields = ("id", "date", "reason")


class PortfolioImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioImage
        fields = ("id", "image", "caption", "order")

class GalleryImageSerializer(serializers.ModelSerializer):
    stylist_name = serializers.CharField(source="stylist.user.get_full_name", read_only=True)
    stylist_title = serializers.CharField(source="stylist.title", read_only=True)
 
    class Meta:
        model = PortfolioImage
        fields = ("id", "image", "caption", "stylist", "stylist_name", "stylist_title")


class StylistProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    avatar = serializers.ImageField(source="user.avatar", read_only=True)
    specialties = ServiceSerializer(many=True, read_only=True)
    availability = AvailabilitySerializer(many=True, read_only=True)
    portfolio = PortfolioImageSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = StylistProfile
        fields = (
            "id", "full_name", "avatar", "salon", "title", "bio",
            "specialties", "years_experience", "is_accepting_bookings",
            "average_rating", "availability", "portfolio",
        )
