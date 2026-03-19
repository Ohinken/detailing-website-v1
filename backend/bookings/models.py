from django.db import models


class Booking(models.Model):
    SERVICE_CHOICES = [
        ("essential_detail", "Essential Detail"),
        ("premium_detail", "Premium Detail"),
        ("showroom_detail", "Showroom Detail"),
        ("maintenance_wash", "Maintenance Wash"),
        ("exterior_detail", "Exterior Detail"),
        ("paint_refresh", "Paint Refresh"),
        ("interior_refresh", "Interior Refresh"),
        ("deep_interior", "Deep Interior"),
        ("seat_carpet_reset", "Seat & Carpet Reset"),
    ]

    SLOT_CHOICES = [
        ("09:00-11:00", "9:00 AM - 11:00 AM"),
        ("11:30-01:30", "11:30 AM - 1:30 PM"),
        ("02:00-04:00", "2:00 PM - 4:00 PM"),
    ]

    customer_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    email = models.EmailField()

    vehicle_make_model = models.CharField(max_length=200)
    detail_location = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)

    service = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    service_price = models.DecimalField(max_digits=8, decimal_places=2)

    booking_date = models.DateField()
    time_slot = models.CharField(max_length=20, choices=SLOT_CHOICES)

    google_event_id = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["booking_date", "time_slot"],
                name="unique_booking_slot"
            )
        ]
        ordering = ["booking_date", "time_slot"]

    def __str__(self):
        return f"{self.customer_name} - {self.booking_date} {self.time_slot}"


class WeeklyAvailability(models.Model):
    DAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    day_of_week = models.IntegerField(choices=DAY_CHOICES, unique=True)
    is_bookable = models.BooleanField(default=False)

    class Meta:
        ordering = ["day_of_week"]

    def __str__(self):
        return f"{self.get_day_of_week_display()} - {'Open' if self.is_bookable else 'Closed'}"


class ClosedDate(models.Model):
    date = models.DateField(unique=True)
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.date} - Closed"


class BlockedTimeSlot(models.Model):
    date = models.DateField()
    time_slot = models.CharField(max_length=20)
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("date", "time_slot")
        ordering = ["date", "time_slot"]

    def __str__(self):
        return f"{self.date} - {self.time_slot}"