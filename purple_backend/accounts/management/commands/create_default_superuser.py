import os

from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = (
        "Idempotently creates (or updates the password of) a superuser from "
        "DJANGO_SUPERUSER_EMAIL / DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_PASSWORD "
        "environment variables. Safe to run on every deploy — skips silently if the "
        "env vars aren't set, and won't error if the user already exists."
    )

    def handle(self, *args, **options):
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not all([email, username, password]):
            self.stdout.write(
                "DJANGO_SUPERUSER_EMAIL / _USERNAME / _PASSWORD not fully set — skipping superuser creation."
            )
            return

        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": username, "is_staff": True, "is_superuser": True},
        )
        user.username = username
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Superuser '{email}' created."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Superuser '{email}' already existed — password/flags refreshed."))