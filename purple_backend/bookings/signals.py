from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.dispatch import send_sms_async
from notifications.messages import customer_booking_confirmation, stylist_new_booking_alert

from .models import Booking


@receiver(post_save, sender=Booking)
def notify_on_booking_created(sender, instance: Booking, created, **kwargs):
    """
    Fires once, right when a booking is first created (not on later status
    updates — confirm/complete/cancel don't re-trigger this). Sends one SMS
    to the customer and one to the stylist, each fire-and-forget so a slow
    or failed SMS gateway never delays or breaks the booking API response.
    """
    if not created:
        return

    if instance.customer.phone:
        send_sms_async(instance.customer.phone, customer_booking_confirmation(instance))

    stylist_phone = instance.stylist.user.phone
    if stylist_phone:
        send_sms_async(stylist_phone, stylist_new_booking_alert(instance))
