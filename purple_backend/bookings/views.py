from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Booking, Review
from .serializers import BookingSerializer, ReviewSerializer


class IsOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if obj.customer_id == request.user.id:
            return True
        stylist_profile = getattr(request.user, "stylist_profile", None)
        return bool(stylist_profile and obj.stylist_id == stylist_profile.id)


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
    filterset_fields = ["status", "salon", "stylist", "date"]

    def get_queryset(self):
        user = self.request.user
        qs = Booking.objects.select_related("customer", "salon", "stylist__user", "service")
        if user.is_staff:
            return qs
        if hasattr(user, "stylist_profile"):
            return qs.filter(stylist=user.stylist_profile)
        return qs.filter(customer=user)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        booking = self.get_object()
        booking.status = Booking.Status.CANCELLED
        booking.save()
        return Response(BookingSerializer(booking).data)

    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm(self, request, pk=None):
        booking = self.get_object()
        booking.status = Booking.Status.CONFIRMED
        booking.save()
        return Response(BookingSerializer(booking).data)

    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        booking = self.get_object()
        booking.status = Booking.Status.COMPLETED
        booking.save()
        return Response(BookingSerializer(booking).data)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """Quick stylist/admin analytics: today, this week, this month counts + revenue."""
        import datetime as dt
        from django.db.models import Sum, Count

        today = dt.date.today()
        week_start = today - dt.timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        qs = self.get_queryset().exclude(status=Booking.Status.CANCELLED)

        def summarize(queryset):
            agg = queryset.aggregate(count=Count("id"), revenue=Sum("price"))
            return {"count": agg["count"] or 0, "revenue": float(agg["revenue"] or 0)}

        return Response({
            "today": summarize(qs.filter(date=today)),
            "this_week": summarize(qs.filter(date__gte=week_start)),
            "this_month": summarize(qs.filter(date__gte=month_start)),
            "upcoming_count": qs.filter(
                date__gte=today, status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED]
            ).count(),
        })

    @action(detail=False, methods=["get"], url_path="upcoming")
    def upcoming(self, request):
        import datetime as dt

        qs = self.get_queryset().filter(
            date__gte=dt.date.today(),
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
        )
        return Response(BookingSerializer(qs, many=True).data)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
 
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
 
    def get_queryset(self):
        return Review.objects.select_related("booking__customer", "booking__service", "booking__stylist__user")
 
    def perform_create(self, serializer):
        booking = serializer.validated_data["booking"]
        if booking.customer_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
 
            raise PermissionDenied("You can only review your own bookings.")
        serializer.save()
 
    @action(detail=False, methods=["get"], url_path="featured", permission_classes=[permissions.AllowAny])
    def featured(self, request):
        """GET /api/bookings/reviews/featured/ — top-rated reviews with a comment, for public display."""
        qs = (
            self.get_queryset()
            .filter(rating__gte=4)
            .exclude(comment="")
            .order_by("-rating", "-created_at")[:6]
        )
        return Response(self.get_serializer(qs, many=True).data)

