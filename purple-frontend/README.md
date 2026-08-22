# Purple — Frontend (React + Vite)

React client for the Purple salon booking platform, wired to the Django REST API.

## Setup
```bash
npm install
cp .env.example .env      # set VITE_API_BASE_URL if your API isn't on 127.0.0.1:8000
npm run dev
```
Make sure the Django backend is running first (see `purple-backend` project),
and run `python manage.py seed_demo` there for sample services/stylists to show up.

## Structure
- `src/api/` — axios client with automatic JWT refresh, plus auth/catalog/booking API modules
- `src/context/AuthContext.jsx` — global auth state (login/register/logout, current user)
- `src/components/` — Navbar, Footer, ProtectedRoute
- `src/pages/` — Landing, Services, ServiceDetail, Stylists, StylistProfile, BookingFlow, Login, Register, Dashboard

## Pages wired to real data
- **Landing** — pulls first 4 services from the API
- **Services / ServiceDetail** — category-grouped service menu, individual service page with a "Book this service" CTA
- **Stylists / StylistProfile** — stylist list + profile with specialties and portfolio
- **BookingFlow** (`/book`) — real 4-step flow: service → stylist → date/time (live slots from `/api/stylists/<id>/slots/`) → confirm (creates a real booking via `/api/bookings/`)
- **Dashboard** (`/dashboard`, protected) — lists the logged-in user's bookings with cancel action
- **Login / Register** — JWT auth against `/api/auth/`

## Auth
JWTs are stored in `localStorage` and auto-refreshed via an axios response interceptor
when a request gets a 401. `AuthContext` exposes `user`, `login`, `register`, `logout`.

## Not yet built
- Payment step in the booking flow (Paystack/MTN MoMo)
- Stylist-facing dashboard (their own bookings/availability management)
- Toast notifications, richer form validation, image upload UI for portfolios
