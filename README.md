# Purple — Backend (Django + DRF)

Beauty salon booking platform API for Accra, Ghana. Men's cuts, women's styling,
lash studio, nails & pedicure — all bookable through one system.

## Apps
- **accounts** — custom `User` model (email login, roles: customer/stylist/admin), JWT auth
- **salons** — salon/studio locations
- **services** — service categories & individual services (price in GHS, duration)
- **stylists** — stylist profiles, weekly availability, time-off, portfolio images, self-service endpoints (`/me/...`), public gallery
- **bookings** — bookings with overlap validation + auto end-time calc, reviews, featured reviews
- **notifications** — SMS dispatch on booking creation (see below)

## Quick start
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py seed_demo
python3 manage.py runserver
```

## SMS notifications

When a booking is created, both the **customer** and the **stylist** automatically
receive an SMS — confirmation for the customer, a new-booking alert for the stylist.
Uses [Arkesel](https://arkesel.com), a Ghana-based SMS gateway that handles local
`+233` numbers and lets you set a custom sender ID (e.g. "Purple" instead of a
random shortcode).

**How it works:**
- `bookings/signals.py` listens for `Booking` creation (not status updates — confirming/
  completing/cancelling a booking doesn't re-send anything) and fires two SMS sends
- `notifications/dispatch.py` sends each SMS in a background thread, so a slow or
  down SMS gateway can never add latency to, or break, the booking API response
- `notifications/sms.py` never raises — any failure (missing API key, network
  error, bad response) is logged and swallowed, not surfaced to the user
- If a customer or stylist has no phone number on file, that SMS is skipped silently

**Setup:**
1. Sign up at [arkesel.com](https://arkesel.com) and grab an API key
2. Set environment variables:

   | Key | Value |
   |---|---|
   | `ARKESEL_API_KEY` | your Arkesel API key |
   | `ARKESEL_SENDER_ID` | e.g. `Purple` (subject to Arkesel's sender ID approval process) |
   | `SMS_ENABLED` | `True` (set to `False` to disable all sending, e.g. in tests) |

Without `ARKESEL_API_KEY` set, the app runs completely normally — bookings still
work, the SMS send is just skipped with a logged warning. This means local dev
and CI never need real credentials.

**Message templates** live in `notifications/messages.py` — edit the wording there;
nothing else needs to change.

**Swapping providers:** everything funnels through `send_sms(to, message)` in
`notifications/sms.py`. Adding a new provider (e.g. Twilio, Hubtel, mNotify) means
adding one new branch there — no changes needed anywhere else in the codebase.

## Media storage (Cloudinary)
Render's filesystem is wiped on every redeploy, so uploaded avatars/portfolio
images need external storage to survive. Set `CLOUDINARY_URL` in production
(sign up free at cloudinary.com) — media automatically routes there instead of
local disk. Leave unset for local dev.

## Admin
Django admin is fully wired and themed purple via `django-admin-interface`:
```bash
python3 manage.py migrate
python3 manage.py seed_admin_theme
```

## Superuser creation without Shell access
Render's free tier doesn't include Shell. Set `DJANGO_SUPERUSER_EMAIL`,
`DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD` as env vars — `build.sh`
runs `create_default_superuser` on every deploy, which is idempotent (safe to
leave in place permanently; skips silently if unset).

## Key API endpoints
| Method | Endpoint | Notes |
|---|---|---|
| POST | `/api/auth/register/` | create account |
| POST | `/api/auth/login/` | returns `access` + `refresh` JWT |
| GET | `/api/salons/` | list studios |
| GET | `/api/services/categories/` | categories with nested services |
| GET | `/api/stylists/` | stylist profiles |
| GET | `/api/stylists/<id>/slots/?date=YYYY-MM-DD&service_duration=60` | free time slots for a day |
| GET | `/api/stylists/gallery/` | portfolio images across all stylists |
| GET | `/api/stylists/me/` | logged-in stylist's own profile |
| GET/POST/DELETE | `/api/stylists/me/availability/` | logged-in stylist manages their own hours |
| GET/POST | `/api/bookings/` | list own bookings / create a booking (**triggers SMS to customer + stylist**) |
| GET | `/api/bookings/stats/` | today/week/month counts + revenue |
| GET | `/api/bookings/reviews/featured/` | top-rated public reviews |
| POST | `/api/bookings/<id>/confirm/` `/complete/` `/cancel/` | status transitions |

## Next steps (not yet built)
- Payment integration (Paystack/MTN MoMo)
- SMS reminders ahead of the appointment (not just at booking time)
- Email notifications alongside SMS
