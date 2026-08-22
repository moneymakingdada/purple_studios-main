from rest_framework.routers import DefaultRouter

from .views import BookingViewSet, ReviewViewSet

router = DefaultRouter()
router.register("reviews", ReviewViewSet, basename="review")
router.register("", BookingViewSet, basename="booking")

urlpatterns = router.urls
