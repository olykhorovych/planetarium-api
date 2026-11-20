from datetime import datetime

from django.db.models import Count, F
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet,
    ReadOnlyModelViewSet,
)

from planetarium.models import (
    AstronomyShow,
    PlanetariumDome,
    Reservation,
    ShowSession,
    ShowTheme,
)
from planetarium.pagination import (
    ReservationPagination,
    ShowSessionPagination,
)
from planetarium.permissions import IsAdminOrIfAuthenticatedReadOnly
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
)


class ShowThemeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class PlanetariumDomeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AstronomyShowViewSet(
    mixins.CreateModelMixin,
    ReadOnlyModelViewSet,
):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""

        return [
            int(str_id) for str_id in qs.split(",")
        ]

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer

        if self.action == "retrieve":
            return AstronomyShowDetailSerializer

        return AstronomyShowSerializer

    def get_queryset(self):
        """Retrieve the astronomy shows with filters"""

        queryset = (
            super().get_queryset()
            .prefetch_related("show_themes")
        )

        title = self.request.query_params.get("title")
        themes = (
            self.request.query_params.get("show_themes")
            or self.request.query_params.get("themes")
        )

        if title:
            queryset = queryset.filter(title__icontains=title)

        if themes:
            queryset = queryset.filter(
                    show_themes__id__in=self._params_to_ints(themes)
            )

        return queryset.distinct()


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
    pagination_class = ShowSessionPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = super().get_queryset()

        date = self.request.query_params.get("date")
        astronomy_show = (
            self.request.query_params.get("astronomy_show")
            or self.request.query_params.get("show")
        )

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(show_time__date=date)

        if astronomy_show:
            queryset = queryset.filter(astronomy_show_id=int(astronomy_show))

        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "astronomy_show__show_themes",
                "tickets",
            )

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer

        if self.action == "retrieve":
            return ShowSessionDetailSerializer

        return ShowSessionSerializer


class ReservationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = (
        Reservation.objects.prefetch_related(
            "tickets__show_session__astronomy_show",
            "tickets__show_session__planetarium_dome"
        )
    )
    serializer_class = ReservationSerializer
    pagination_class = ReservationPagination
    permission_classes = (IsAuthenticated,)

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
