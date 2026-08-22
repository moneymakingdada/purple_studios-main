from django.core.management.base import BaseCommand
from django.utils.text import slugify

from accounts.models import User
from salons.models import Salon
from services.models import Service, ServiceCategory
from stylists.models import Availability, StylistProfile


class Command(BaseCommand):
    help = "Seed the database with demo Purple data: a salon, categories, services, and a stylist."

    def handle(self, *args, **options):
        salon, _ = Salon.objects.get_or_create(
            slug="purple-east-legon",
            defaults=dict(
                name="Purple East Legon",
                city="Accra",
                region="greater_accra",
                address="12 Lagos Avenue, East Legon, Accra",
                phone="+233241234567",
            ),
        )

        categories = {
            "Men's Cuts": ["Skin Fade", "Beard Trim & Line-up", "Classic Taper"],
            "Women's Styling": ["Silk Press", "Full Colour", "Braids & Weave-in"],
            "Lash Studio": ["Classic Set", "Hybrid Set", "Full Volume Set"],
            "Nails & Pedicure": ["Gel Pedicure", "Classic Manicure", "Nail Art Add-on"],
        }
        prices = {
            "Skin Fade": 60, "Beard Trim & Line-up": 30, "Classic Taper": 50,
            "Silk Press": 150, "Full Colour": 350, "Braids & Weave-in": 250,
            "Classic Set": 250, "Hybrid Set": 320, "Full Volume Set": 400,
            "Gel Pedicure": 120, "Classic Manicure": 80, "Nail Art Add-on": 40,
        }
        durations = {
            "Skin Fade": 45, "Beard Trim & Line-up": 20, "Classic Taper": 40,
            "Silk Press": 90, "Full Colour": 150, "Braids & Weave-in": 180,
            "Classic Set": 75, "Hybrid Set": 90, "Full Volume Set": 120,
            "Gel Pedicure": 60, "Classic Manicure": 45, "Nail Art Add-on": 20,
        }

        for order, (cat_name, service_names) in enumerate(categories.items()):
            category, _ = ServiceCategory.objects.get_or_create(
                name=cat_name, defaults=dict(slug=slugify(cat_name), order=order)
            )
            for name in service_names:
                Service.objects.get_or_create(
                    slug=slugify(f"{cat_name}-{name}"),
                    defaults=dict(
                        category=category,
                        name=name,
                        price=prices[name],
                        duration_minutes=durations[name],
                        audience="unisex",
                    ),
                )

        stylist_user, created = User.objects.get_or_create(
            email="ama.k@purple.com",
            defaults=dict(username="ama_k", first_name="Ama", last_name="Konadu", role=User.Role.STYLIST),
        )
        if created:
            stylist_user.set_password("Purple2026!")
            stylist_user.save()

        profile, _ = StylistProfile.objects.get_or_create(
            user=stylist_user,
            defaults=dict(salon=salon, title="Senior colour & cut specialist", years_experience=7),
        )

        for weekday in range(0, 6):  # Mon-Sat
            Availability.objects.get_or_create(
                stylist=profile, weekday=weekday,
                defaults=dict(start_time="09:00", end_time="18:00"),
            )

        self.stdout.write(self.style.SUCCESS("Demo data seeded: 1 salon, 4 categories, 12 services, 1 stylist."))
