"""
All the numbers behind the admin dashboard. Kept as plain functions returning
JSON-serializable data so the template can drop them straight into Chart.js.
"""
import datetime as dt
import json

from django.db.models import Avg, Count, Sum
from django.utils import timezone

from accounts.models import User
from bookings.models import Booking, Review
from stylists.models import StylistProfile


def _daterange_labels(days: int, end_date: dt.date):
    return [(end_date - dt.timedelta(days=i)) for i in range(days - 1, -1, -1)]


def get_dashboard_stats():
    today = timezone.localdate()
    week_start = today - dt.timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    active_bookings = Booking.objects.exclude(status=Booking.Status.CANCELLED)

    def summarize(qs):
        agg = qs.aggregate(count=Count("id"), revenue=Sum("price"))
        return {"count": agg["count"] or 0, "revenue": float(agg["revenue"] or 0)}

    stats = {
        "today": summarize(active_bookings.filter(date=today)),
        "this_week": summarize(active_bookings.filter(date__gte=week_start)),
        "this_month": summarize(active_bookings.filter(date__gte=month_start)),
        "total_customers": User.objects.filter(role=User.Role.CUSTOMER).count(),
        "total_stylists": StylistProfile.objects.count(),
        "new_customers_this_week": User.objects.filter(
            role=User.Role.CUSTOMER, created_at__date__gte=week_start
        ).count(),
        "pending_count": Booking.objects.filter(status=Booking.Status.PENDING).count(),
        "average_rating": round(Review.objects.aggregate(avg=Avg("rating"))["avg"] or 0, 2),
    }

    last_14_days = _daterange_labels(14, today)
    bookings_by_day = {
        row["date"]: row["count"]
        for row in active_bookings.filter(date__gte=last_14_days[0]).values("date").annotate(count=Count("id"))
    }
    trend_labels = [d.strftime("%b %d") for d in last_14_days]
    trend_values = [bookings_by_day.get(d, 0) for d in last_14_days]

    status_counts = dict(Booking.objects.values_list("status").annotate(count=Count("id")).order_by())
    status_labels = [Booking.Status(s).label for s in status_counts.keys()]
    status_values = list(status_counts.values())

    top_services = (
        active_bookings.filter(date__gte=month_start)
        .values("service__name").annotate(count=Count("id")).order_by("-count")[:5]
    )
    top_service_labels = [row["service__name"] for row in top_services]
    top_service_values = [row["count"] for row in top_services]

    top_stylists = (
        active_bookings.filter(date__gte=month_start)
        .values("stylist__user__first_name", "stylist__user__last_name")
        .annotate(revenue=Sum("price")).order_by("-revenue")[:5]
    )
    top_stylist_labels = [
        f"{row['stylist__user__first_name']} {row['stylist__user__last_name']}".strip()
        for row in top_stylists
    ]
    top_stylist_values = [float(row["revenue"] or 0) for row in top_stylists]

    recent_bookings = (
        Booking.objects.select_related("customer", "stylist__user", "service").order_by("-created_at")[:8]
    )

    return {
        "stats": stats,
        "trend_labels": json.dumps(trend_labels),
        "trend_values": json.dumps(trend_values),
        "status_labels": json.dumps(status_labels),
        "status_values": json.dumps(status_values),
        "top_service_labels": json.dumps(top_service_labels),
        "top_service_values": json.dumps(top_service_values),
        "top_stylist_labels": json.dumps(top_stylist_labels),
        "top_stylist_values": json.dumps(top_stylist_values),
        "recent_bookings": recent_bookings,
    }
