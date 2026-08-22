"""Plain-text SMS templates. Kept short — most SMS gateways bill per 160-char segment."""


def customer_booking_confirmation(booking) -> str:
    return (
        f"Hi {booking.customer.first_name or booking.customer.username}, your Purple booking is confirmed: "
        f"{booking.service.name} with {booking.stylist.user.get_full_name()} "
        f"on {booking.date.strftime('%a %d %b')} at {booking.start_time.strftime('%I:%M %p')}. "
        f"See you soon!"
    )


def stylist_new_booking_alert(booking) -> str:
    return (
        f"New booking, {booking.stylist.user.first_name or booking.stylist.user.username}: "
        f"{booking.customer.get_full_name() or booking.customer.username} booked {booking.service.name} "
        f"on {booking.date.strftime('%a %d %b')} at {booking.start_time.strftime('%I:%M %p')}."
    )
