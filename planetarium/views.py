from django.db.models import F, Count
from rest_framework.viewsets import ModelViewSet

from planetarium.models import (
    AstronomyShow,
    PlanetariumDome,
    Reservation,
    ShowSession,
    ShowTheme,
    Ticket,
)
from planetarium.serializers import (
    AstronomyShowDetailSerializer,
    AstronomyShowListSerializer,
    AstronomyShowSerializer,
    PlanetariumDomeSerializer,
    ReservationListSerializer,
    ReservationSerializer,
    ShowSessionDetailSerializer,
    ShowSessionListSerializer,
    ShowSessionSerializer,
    ShowThemeSerializer,
    TicketSerializer,
)


class ShowThemeViewSet(ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class PlanetariumDomeViewSet(ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class AstronomyShowViewSet(ModelViewSet):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer

        if self.action == "retrieve":
            return AstronomyShowDetailSerializer

        return AstronomyShowSerializer

    def get_queryset(self):
        return (
            super().get_queryset()
            .prefetch_related("show_themes")
        )


class ShowSessionViewSet(ModelViewSet):
    queryset = ShowSession.objects.select_related(
        "astronomy_show",
        "planetarium_dome"
    ).annotate(
        tickets_available=(
            F("planetarium_dome__rows")
            * F("planetarium_dome__seats_in_row")
            - Count("tickets")
        )
    )
    serializer_class = ShowSessionSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer

        if self.action == "retrieve":
            return ShowSessionDetailSerializer

        return ShowSessionSerializer


class ReservationViewSet(ModelViewSet):
    queryset = (
        Reservation.objects.prefetch_related(
            "tickets__show_session__astronomy_show",
            "tickets__show_session__planetarium_dome"
        )
    )
    serializer_class = ReservationSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer

        return ReservationSerializer

    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(user=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
