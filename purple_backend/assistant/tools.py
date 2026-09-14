"""
Tool implementations the WhatsApp agent can call, plus their JSON-schema
definitions for Anthropic's tool-use API. Each tool function takes
(session, **args) and returns a small JSON-serializable dict — the agent
reads that result and decides what to say or do next.

Kept deliberately close to the ORM (not going through the DRF HTTP API) since
this all runs server-side in the same process — no auth handshake needed,
just direct model access scoped to the session's own customer.
"""
import datetime as dt

from django.db.models import Q

from bookings.models import Booking
from salons.models import Salon
from services.models import Service
from stylists.models import StylistProfile


class ToolError(Exception):
    """Raised for expected, user-facing problems (e.g. 'no such stylist') —
    the agent shows the message to the customer rather than treating it as
    a crash."""


def _fuzzy_service(name: str) -> Service:
    service = Service.objects.filter(is_active=True).filter(
        Q(name__icontains=name) | Q(slug__icontains=name.replace(" ", "-"))
    ).first()
    if not service:
        raise ToolError(f"I couldn't find a service matching '{name}'. Try list_services to see what's available.")
    return service


def _fuzzy_stylist(name: str) -> StylistProfile:
    stylist = StylistProfile.objects.filter(is_accepting_bookings=True).filter(
        Q(user__first_name__icontains=name) | Q(user__last_name__icontains=name)
    ).first()
    if not stylist:
        raise ToolError(f"I couldn't find a stylist matching '{name}'. Try list_stylists to see who's available.")
    return stylist


def _default_salon() -> Salon:
    salon = Salon.objects.filter(is_active=True).first()
    if not salon:
        raise ToolError("No active studio is configured right now.")
    return salon


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def list_services(session, **kwargs):
    services = Service.objects.filter(is_active=True).select_related("category")
    return {
        "services": [
            {"name": s.name, "category": s.category.name, "price_ghs": float(s.price),
             "duration_minutes": s.duration_minutes, "audience": s.audience}
            for s in services
        ]
    }


def list_stylists(session, **kwargs):
    stylists = StylistProfile.objects.filter(is_accepting_bookings=True).select_related("user").prefetch_related("specialties")
    return {
        "stylists": [
            {"name": s.user.get_full_name(), "title": s.title, "years_experience": s.years_experience,
             "average_rating": s.average_rating,
             "specialties": [sp.name for sp in s.specialties.all()]}
            for s in stylists
        ]
    }


def check_slots(session, stylist_name: str, service_name: str, date: str, **kwargs):
    stylist = _fuzzy_stylist(stylist_name)
    service = _fuzzy_service(service_name)
    try:
        target_date = dt.date.fromisoformat(date)
    except ValueError:
        raise ToolError(f"'{date}' isn't a valid date — use YYYY-MM-DD.")

    if target_date < dt.date.today():
        raise ToolError("That date is in the past.")

    if stylist.time_off.filter(date=target_date).exists():
        return {"date": date, "stylist": stylist.user.get_full_name(), "slots": [], "note": "Stylist is off that day."}

    windows = stylist.availability.filter(weekday=target_date.weekday())
    if not windows.exists():
        return {"date": date, "stylist": stylist.user.get_full_name(), "slots": [], "note": "Stylist doesn't work that day of the week."}

    busy = Booking.objects.filter(
        stylist=stylist, date=target_date, status__in=["pending", "confirmed"]
    ).values_list("start_time", "end_time")

    step = dt.timedelta(minutes=30)
    slot_length = dt.timedelta(minutes=service.duration_minutes)
    free_slots = []
    for window in windows:
        cursor = dt.datetime.combine(target_date, window.start_time)
        window_end = dt.datetime.combine(target_date, window.end_time)
        while cursor + slot_length <= window_end:
            slot_start, slot_end = cursor.time(), (cursor + slot_length).time()
            if not any(slot_start < b_end and slot_end > b_start for b_start, b_end in busy):
                free_slots.append(slot_start.strftime("%H:%M"))
            cursor += step

    return {"date": date, "stylist": stylist.user.get_full_name(), "service": service.name, "slots": free_slots}


def book_appointment(session, stylist_name: str, service_name: str, date: str, time: str, customer_name: str = None, **kwargs):
    stylist = _fuzzy_stylist(stylist_name)
    service = _fuzzy_service(service_name)
    salon = _default_salon()

    try:
        target_date = dt.date.fromisoformat(date)
        start_time = dt.datetime.strptime(time, "%H:%M").time()
    except ValueError:
        raise ToolError("Date must be YYYY-MM-DD and time must be HH:MM (24-hour).")

    customer = session.customer
    if customer is None:
        if not customer_name:
            raise ToolError(
                "I don't have this customer's name yet — ask for their name before booking, "
                "then call book_appointment again with customer_name set."
            )
        from accounts.models import User

        first, _, last = customer_name.partition(" ")
        customer = User.objects.create(
            username=f"wa_{session.wa_phone.lstrip('+')}",
            email=f"wa_{session.wa_phone.lstrip('+')}@whatsapp.purple.local",
            first_name=first, last_name=last,
            phone=session.wa_phone, role=User.Role.CUSTOMER,
        )
        session.customer = customer
        session.save(update_fields=["customer"])

    end_dt = dt.datetime.combine(target_date, start_time) + dt.timedelta(minutes=service.duration_minutes)

    try:
        booking = Booking.objects.create(
            customer=customer, salon=salon, stylist=stylist, service=service,
            date=target_date, start_time=start_time, end_time=end_dt.time(), price=service.price,
        )
    except Exception as exc:
        raise ToolError(f"Couldn't book that slot — it may have just been taken. ({exc})")

    return {
        "booking_id": str(booking.id), "status": booking.status,
        "service": service.name, "stylist": stylist.user.get_full_name(),
        "date": date, "time": time, "price_ghs": float(service.price),
    }


def get_upcoming_bookings(session, **kwargs):
    if not session.customer:
        return {"bookings": [], "note": "No account linked yet — nothing booked."}

    bookings = Booking.objects.filter(
        customer=session.customer, date__gte=dt.date.today(),
        status__in=["pending", "confirmed"],
    ).select_related("service", "stylist__user").order_by("date", "start_time")

    return {
        "bookings": [
            {"booking_id": str(b.id), "service": b.service.name, "stylist": b.stylist.user.get_full_name(),
             "date": str(b.date), "time": b.start_time.strftime("%H:%M"), "status": b.status}
            for b in bookings
        ]
    }


def cancel_appointment(session, booking_id: str, **kwargs):
    if not session.customer:
        raise ToolError("No account linked — there's nothing to cancel.")

    booking = Booking.objects.filter(id=booking_id, customer=session.customer).first()
    if not booking:
        raise ToolError("Couldn't find a booking with that ID for this customer.")

    booking.status = Booking.Status.CANCELLED
    booking.save()
    return {"booking_id": str(booking.id), "status": "cancelled"}


# ---------------------------------------------------------------------------
# Registry + JSON schemas for Anthropic's tool-use API
# ---------------------------------------------------------------------------

TOOL_FUNCTIONS = {
    "list_services": list_services,
    "list_stylists": list_stylists,
    "check_slots": check_slots,
    "book_appointment": book_appointment,
    "get_upcoming_bookings": get_upcoming_bookings,
    "cancel_appointment": cancel_appointment,
}

TOOL_SCHEMAS = [
    {
        "name": "list_services",
        "description": "List every active service Purple offers, with price (GHS) and duration.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_stylists",
        "description": "List every stylist currently accepting bookings, with their title and specialties.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "check_slots",
        "description": "Check a stylist's open time slots for a given service on a given date.",
        "input_schema": {
            "type": "object",
            "properties": {
                "stylist_name": {"type": "string", "description": "Stylist's first or last name"},
                "service_name": {"type": "string", "description": "Service name, e.g. 'Skin Fade'"},
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
            },
            "required": ["stylist_name", "service_name", "date"],
        },
    },
    {
        "name": "book_appointment",
        "description": (
            "Create a booking for the current customer. If this is a brand-new customer "
            "(no name known yet), ask for their name first and pass it as customer_name."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "stylist_name": {"type": "string"},
                "service_name": {"type": "string"},
                "date": {"type": "string", "description": "YYYY-MM-DD"},
                "time": {"type": "string", "description": "HH:MM, 24-hour"},
                "customer_name": {"type": "string", "description": "Only needed the first time a new customer books"},
            },
            "required": ["stylist_name", "service_name", "date", "time"],
        },
    },
    {
        "name": "get_upcoming_bookings",
        "description": "List the current customer's upcoming (pending or confirmed) bookings.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "cancel_appointment",
        "description": "Cancel one of the current customer's bookings by its booking_id.",
        "input_schema": {
            "type": "object",
            "properties": {"booking_id": {"type": "string"}},
            "required": ["booking_id"],
        },
    },
]
