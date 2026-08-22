from rest_framework.routers import DefaultRouter

from .views import SalonViewSet

router = DefaultRouter()
router.register("", SalonViewSet, basename="salon")

urlpatterns = router.urls
