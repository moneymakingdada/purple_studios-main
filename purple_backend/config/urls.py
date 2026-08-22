import os
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

admin.site.site_header = settings.ADMIN_SITE_HEADER
admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.index_title = settings.ADMIN_INDEX_TITLE


def index(request):
    return JsonResponse({
        "status": "ok",
        "service": "Purple backend",
        "admin": request.build_absolute_uri("/admin/"),
        "api": {
            "auth": request.build_absolute_uri("/api/auth/"),
            "salons": request.build_absolute_uri("/api/salons/"),
            "services": request.build_absolute_uri("/api/services/"),
            "stylists": request.build_absolute_uri("/api/stylists/"),
            "bookings": request.build_absolute_uri("/api/bookings/"),
        },
    })


urlpatterns = [
    path("", index, name="index"),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/salons/", include("salons.urls")),
    path("api/services/", include("services.urls")),
    path("api/stylists/", include("stylists.urls")),
    path("api/bookings/", include("bookings.urls")),
]

if not os.environ.get("CLOUDINARY_URL"):
    # Serve media from local disk even outside DEBUG. Django never does this by
    # default in production — fine for small scale / non-Render hosts with a
    # persistent disk, but on Render specifically these files won't survive a
    # redeploy. Set CLOUDINARY_URL in production to avoid that entirely.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)