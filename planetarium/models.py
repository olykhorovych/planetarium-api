from django.conf import settings
from django.core.validators import MinValueValidator, ValidationError
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

    @staticmethod
    def validate_ticket(row, seat, planetarium_dome, error_to_raise):
        for (
            ticket_attr_value,
            ticket_attr_name,
            planetarium_dome_attr_name,
        ) in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(planetarium_dome, planetarium_dome_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {planetarium_dome_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.show_session.planetarium_dome,
            ValidationError,
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
