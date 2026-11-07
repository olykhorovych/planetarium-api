from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline
from django.db.models import QuerySet
from django.http import HttpRequest

from planetarium.models import (
    AstronomyShow,
    PlanetariumDome,
    Reservation,
    ShowSession,
    ShowTheme,
    Ticket,
)


@admin.register(ShowTheme)
class ShowThemeAdmin(ModelAdmin):
    search_fields = ("name",)


@admin.register(AstronomyShow)
class AstronomyShowAdmin(ModelAdmin):
    list_display = ("title", "description", "display_show_themes")
    search_fields = ("title",)
    filter_horizontal = ("show_themes",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super().get_queryset(request)
            .prefetch_related("show_themes")
        )

    @admin.display(description="Show Themes")
    def display_show_themes(self, obj: AstronomyShow) -> str:
        return ", ".join(
            theme.name for theme in obj.show_themes.all()
        )


@admin.register(PlanetariumDome)
class PlanetariumDomeAdmin(ModelAdmin):
    list_display = ("name", "rows", "seats_in_row", "capacity")
    search_fields = ("name",)


class TicketInline(TabularInline):
    model = Ticket
    extra = 1


@admin.register(Reservation)
class ReservationAdmin(ModelAdmin):
    list_display = ("id", "user", "created_at")
    list_select_related = ("user",)
    list_filter = ("created_at",)
    search_fields = ("user__username",)
    inlines = (TicketInline,)


@admin.register(ShowSession)
class ShowSessionAdmin(ModelAdmin):
    list_display = (
        "astronomy_show__title",
        "planetarium_dome__name",
        "show_time",
    )
    list_select_related = ("astronomy_show", "planetarium_dome")
    list_filter = ("show_time", "astronomy_show", "planetarium_dome")


@admin.register(Ticket)
class TicketAdmin(ModelAdmin):
    list_display = (
        "show_session",
        "reservation",
        "reservation__user",
        "row",
        "seat",
    )
    list_select_related = (
        "show_session__astronomy_show",
        "reservation__user",
    )
    search_fields = ("show_session__astronomy_show__title",)
    list_filter = ("reservation__created_at",)
    fieldsets = (
        ("Booking Information", {
            "fields": ("show_session", "reservation"),
        }),
        ("Seat Information", {
            "fields": (("row", "seat"),),
        }),
    )
