from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    GalleryListView,
    MyAvailabilityViewSet,
    MyPortfolioViewSet,
    MyStylistProfileView,
    MyTimeOffViewSet,
    StylistProfileViewSet,
)

router = DefaultRouter()
router.register("me/availability", MyAvailabilityViewSet, basename="my-availability")
router.register("me/time-off", MyTimeOffViewSet, basename="my-timeoff")
router.register("me/portfolio", MyPortfolioViewSet, basename="my-portfolio")
router.register("", StylistProfileViewSet, basename="stylist")

urlpatterns = [
    path("me/", MyStylistProfileView.as_view(), name="my-stylist-profile"),

    path("gallery/", GalleryListView.as_view(), name="gallery"),
] + router.urls
