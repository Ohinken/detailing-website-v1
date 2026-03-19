from django.contrib import admin
from .models import Booking, WeeklyAvailability, ClosedDate, BlockedTimeSlot


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "customer_name",
        "service",
        "booking_date",
        "time_slot",
        "phone",
        "email",
    )
    list_filter = ("service", "booking_date", "time_slot")
    search_fields = ("customer_name", "phone", "email", "vehicle_make_model")


@admin.register(WeeklyAvailability)
class WeeklyAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("day_of_week", "is_bookable")
    list_editable = ("is_bookable",)


@admin.register(ClosedDate)
class ClosedDateAdmin(admin.ModelAdmin):
    list_display = ("date", "reason")


@admin.register(BlockedTimeSlot)
class BlockedTimeSlotAdmin(admin.ModelAdmin):
    list_display = ("date", "time_slot", "reason")
    list_filter = ("date",)