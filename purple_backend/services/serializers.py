from rest_framework import serializers

from .models import Service, ServiceCategory


class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Service
        fields = (
            "id", "category", "category_name", "name", "slug", "description",
            "audience", "duration_minutes", "price", "image", "is_active",
        )


class ServiceCategorySerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceCategory
        fields = ("id", "name", "slug", "icon", "order", "services")
