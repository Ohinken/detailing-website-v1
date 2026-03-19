from rest_framework import serializers
from .models import Booking, WeeklyAvailability, ClosedDate, BlockedTimeSlot


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "customer_name",
            "phone",
            "email",
            "vehicle_make_model",
            "detail_location",
            "notes",
            "service",
            "service_price",
            "booking_date",
            "time_slot",
            "google_event_id",
            "created_at",
        ]
        read_only_fields = ["id", "google_event_id", "created_at"]

    def validate(self, data):
        booking_date = data.get("booking_date")
        time_slot = data.get("time_slot")

        weekday = booking_date.weekday()

        weekly_rule = WeeklyAvailability.objects.filter(day_of_week=weekday).first()
        if not weekly_rule or not weekly_rule.is_bookable:
            raise serializers.ValidationError(
                {"error": "This day is not available for booking."}
            )

        if ClosedDate.objects.filter(date=booking_date).exists():
            raise serializers.ValidationError(
                {"error": "This date is closed for booking."}
            )

        if BlockedTimeSlot.objects.filter(date=booking_date, time_slot=time_slot).exists():
            raise serializers.ValidationError(
                {"error": "This time slot is unavailable."}
            )

        if Booking.objects.filter(booking_date=booking_date, time_slot=time_slot).exists():
            raise serializers.ValidationError(
                {"error": "That time slot is already booked."}
            )

        return data