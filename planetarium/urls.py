from django.urls import path, include

from rest_framework.routers import DefaultRouter

from planetarium.views import (
    AstronomyShowViewSet,
    ReservationViewSet,
    ShowSessionViewSet,
    ShowThemeViewSet,
    PlanetariumDomeViewSet,
)


router = DefaultRouter()
router.register("show_themes", ShowThemeViewSet)
router.register("planetarium_domes", PlanetariumDomeViewSet)
router.register("astronomy_shows", AstronomyShowViewSet)
router.register("show_sessions", ShowSessionViewSet)
router.register("reservations", ReservationViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "planetarium"
