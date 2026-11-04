from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class ShowTheme(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=255)
    rows = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    seats_in_row = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return f"{self.name} ({self.capacity} seats)"

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row


class AstronomyShow(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    show_themes = models.ManyToManyField(
        ShowTheme,
        related_name="astronomy_shows"
    )

    class Meta:
        ordering = ("title", )

    def __str__(self):
        return self.title


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    class Meta:
        ordering = ("-created_at", )

    def __str__(self):
        return (
            f"Reservation #{self.pk} "
            f"({self.created_at:%Y-%m-%d %H:%M})"
        )


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(
        AstronomyShow,
        on_delete=models.CASCADE,
        related_name="show_sessions"
    )
    planetarium_dome = models.ForeignKey(
        PlanetariumDome,
        on_delete=models.CASCADE,
        related_name="show_sessions"
    )
    show_time = models.DateTimeField()

    class Meta:
        ordering = ("-show_time", )

    def __str__(self):
        return (
            f"{self.astronomy_show.title} "
            f"({self.show_time:%Y-%m-%d %H:%M})"
        )


class Ticket(models.Model):
    row = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    seat = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    show_session = models.ForeignKey(
        ShowSession,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        ordering = ("row", "seat")
        constraints = [
            models.UniqueConstraint(
                fields=("show_session", "row", "seat"),
                name="unique_seat_per_show_session",
            )
        ]

    def __str__(self):
        return (
            f"Ticket for {self.show_session} "
            f"(row: {self.row}, seat: {self.seat})"
        )
