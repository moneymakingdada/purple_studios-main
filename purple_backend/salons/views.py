from rest_framework import permissions, viewsets

from .models import Salon
from .serializers import SalonSerializer


class SalonViewSet(viewsets.ModelViewSet):
    queryset = Salon.objects.filter(is_active=True)
    serializer_class = SalonSerializer
    lookup_field = "slug"
    filterset_fields = ["city", "region"]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Salon.objects.all()
        return Salon.objects.filter(is_active=True)
