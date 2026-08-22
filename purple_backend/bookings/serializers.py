from rest_framework import serializers

from services.models import Service

from .models import Booking, Review


class ReviewSerializer(serializers.ModelSerializer):
    customer_first_name = serializers.CharField(source="booking.customer.first_name", read_only=True)
    service_name = serializers.CharField(source="booking.service.name", read_only=True)
    stylist_name = serializers.CharField(source="booking.stylist.user.get_full_name", read_only=True)
 
    class Meta:
        model = Review
        fields = (
            "id", "booking", "rating", "comment", "created_at",
            "customer_first_name", "service_name", "stylist_name",
        )
        read_only_fields = ("id", "created_at")


class BookingSerializer(serializers.ModelSerializer):
    review = ReviewSerializer(read_only=True)
    customer_name = serializers.CharField(source="customer.get_full_name", read_only=True)
    stylist_name = serializers.CharField(source="stylist.user.get_full_name", read_only=True)
    service_name = serializers.CharField(source="service.name", read_only=True)
    salon_name = serializers.CharField(source="salon.name", read_only=True)

    class Meta:
        model = Booking
        fields = (
            "id", "customer", "customer_name", "salon", "salon_name",
            "stylist", "stylist_name", "service", "service_name",
            "date", "start_time", "end_time", "status", "price", "notes",
            "created_at", "review",
        )
        read_only_fields = ("id", "customer", "price", "end_time", "created_at")

    def create(self, validated_data):
        import datetime as dt

        service: Service = validated_data["service"]
        start_dt = dt.datetime.combine(validated_data["date"], validated_data["start_time"])
        end_dt = start_dt + dt.timedelta(minutes=service.duration_minutes)
        validated_data["end_time"] = end_dt.time()
        validated_data["price"] = service.price
        validated_data["customer"] = self.context["request"].user
        return super().create(validated_data)
