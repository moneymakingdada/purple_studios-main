from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from notifications.sms import send_sms


class Command(BaseCommand):
    help = (
        "Sends a single test SMS to the given phone number, so you can verify "
        "ARKESEL_API_KEY / ARKESEL_SENDER_ID are working without going through "
        "the full registration + booking flow. Example:\n"
        "  python manage.py test_sms +233241234567\n"
        "  python manage.py test_sms +233241234567 --message \"Custom text here\""
    )

    def add_arguments(self, parser):
        parser.add_argument("phone", type=str, help="Destination phone number, e.g. +233241234567")
        parser.add_argument(
            "--message",
            type=str,
            default=None,
            help="Custom message text. Defaults to a generic Purple test message.",
        )

    def handle(self, *args, **options):
        phone = options["phone"]
        message = options["message"] or "This is a test SMS from Purple. If you got this, SMS sending is working!"

        if not phone.startswith("+"):
            raise CommandError(
                f"'{phone}' doesn't look like it's in international format. "
                f"Use e.g. +233241234567 (Ghana), including the country code."
            )

        self.stdout.write(f"SMS_ENABLED = {settings.SMS_ENABLED}")
        self.stdout.write(f"SMS_PROVIDER = {settings.SMS_PROVIDER}")
        self.stdout.write(f"ARKESEL_SENDER_ID = {settings.ARKESEL_SENDER_ID}")
        self.stdout.write(f"ARKESEL_API_KEY set? = {bool(settings.ARKESEL_API_KEY)}")
        self.stdout.write("")
        self.stdout.write(f"Sending to {phone}: \"{message}\"")

        success = send_sms(phone, message)

        if success:
            self.stdout.write(self.style.SUCCESS(f"✓ Sent successfully to {phone}."))
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"✗ Send failed — check the log line above for the reason "
                    f"(missing API key, network error, or Arkesel rejected the request)."
                )
            )
