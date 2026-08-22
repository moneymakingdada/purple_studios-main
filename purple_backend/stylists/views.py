import datetime as dt

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Availability, PortfolioImage, StylistProfile, TimeOff
from .permissions import IsStylist
from .serializers import (
    AvailabilitySerializer,
    GalleryImageSerializer,
    PortfolioImageSerializer,
    StylistProfileSerializer,
    TimeOffSerializer,
)


class StylistProfileViewSet(viewsets.ModelViewSet):
    queryset = StylistProfile.objects.select_related("user", "salon").prefetch_related(
        "specialties", "availability", "portfolio"
    )
    serializer_class = StylistProfileSerializer
    filterset_fields = ["salon", "is_accepting_bookings"]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @action(detail=True, methods=["get"], url_path="slots")
    def slots(self, request, pk=None):
        """GET /api/stylists/<id>/slots/?date=YYYY-MM-DD&service_duration=60"""
        from bookings.models import Booking  # local import avoids circularity

        stylist = self.get_object()
        date_str = request.query_params.get("date")
        duration = int(request.query_params.get("service_duration", 60))
        if not date_str:
            return Response({"detail": "date query param is required, e.g. ?date=2026-07-14"}, status=400)

        target_date = dt.date.fromisoformat(date_str)

        if stylist.time_off.filter(date=target_date).exists():
            return Response({"date": date_str, "slots": []})

        windows = stylist.availability.filter(weekday=target_date.weekday())
        if not windows.exists():
            return Response({"date": date_str, "slots": []})

        busy = Booking.objects.filter(
            stylist=stylist,
            date=target_date,
            status__in=["pending", "confirmed"],
        ).values_list("start_time", "end_time")

        step = dt.timedelta(minutes=30)
        slot_length = dt.timedelta(minutes=duration)
        free_slots = []

        for window in windows:
            cursor = dt.datetime.combine(target_date, window.start_time)
            window_end = dt.datetime.combine(target_date, window.end_time)
            while cursor + slot_length <= window_end:
                slot_start = cursor.time()
                slot_end = (cursor + slot_length).time()
                overlaps = any(
                    slot_start < b_end and slot_end > b_start
                    for b_start, b_end in busy
                )
                if not overlaps:
                    free_slots.append(slot_start.strftime("%H:%M"))
                cursor += step

        return Response({"date": date_str, "slots": free_slots})


class MyStylistProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/stylists/me/ — the logged-in stylist's own profile."""
    serializer_class = StylistProfileSerializer
    permission_classes = [IsStylist]

    def get_object(self):
        return self.request.user.stylist_profile


class MyAvailabilityViewSet(viewsets.ModelViewSet):
    """CRUD /api/stylists/me/availability/ — scoped to the logged-in stylist only."""
    serializer_class = AvailabilitySerializer
    permission_classes = [IsStylist]

    def get_queryset(self):
        return Availability.objects.filter(stylist=self.request.user.stylist_profile)

    def perform_create(self, serializer):
        serializer.save(stylist=self.request.user.stylist_profile)


class MyTimeOffViewSet(viewsets.ModelViewSet):
    """CRUD /api/stylists/me/time-off/ — scoped to the logged-in stylist only."""
    serializer_class = TimeOffSerializer
    permission_classes = [IsStylist]

    def get_queryset(self):
        return TimeOff.objects.filter(stylist=self.request.user.stylist_profile)

    def perform_create(self, serializer):
        serializer.save(stylist=self.request.user.stylist_profile)


class MyPortfolioViewSet(viewsets.ModelViewSet):
    """CRUD /api/stylists/me/portfolio/ — scoped to the logged-in stylist only."""
    serializer_class = PortfolioImageSerializer
    permission_classes = [IsStylist]

    def get_queryset(self):
        return PortfolioImage.objects.filter(stylist=self.request.user.stylist_profile)

    def perform_create(self, serializer):
        serializer.save(stylist=self.request.user.stylist_profile)


class GalleryListView(generics.ListAPIView):
    """GET /api/stylists/gallery/ — every portfolio image across all stylists, public, newest first."""
    serializer_class = GalleryImageSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ["stylist"]

    def get_queryset(self):
        return (
            PortfolioImage.objects.select_related("stylist__user")
            .filter(stylist__is_accepting_bookings=True)
            .order_by("-id")
        )