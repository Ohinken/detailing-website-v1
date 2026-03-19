from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

from django.conf import settings

from .models import (
    Booking,
    WeeklyAvailability,
    ClosedDate,
    BlockedTimeSlot,
)
from .serializers import BookingSerializer


# -------------------------
# AVAILABLE SLOTS
# -------------------------
@api_view(["GET"])
def available_slots(request):
    date_str = request.GET.get("date")

    if not date_str:
        return Response({"error": "Date is required."}, status=400)

    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "Invalid date format."}, status=400)

    weekday = selected_date.weekday()

    weekly_rule = WeeklyAvailability.objects.filter(day_of_week=weekday).first()
    if not weekly_rule or not weekly_rule.is_bookable:
        return Response(
            {
                "is_bookable_day": False,
                "available_slots": [],
                "message": "This day is not available for booking.",
            }
        )

    if ClosedDate.objects.filter(date=selected_date).exists():
        return Response(
            {
                "is_bookable_day": False,
                "available_slots": [],
                "message": "This date is closed.",
            }
        )

    all_slots = [
        ("09:00-11:00", "9:00 AM - 11:00 AM"),
        ("11:30-01:30", "11:30 AM - 1:30 PM"),
        ("02:00-04:00", "2:00 PM - 4:00 PM"),
    ]

    booked_slots = Booking.objects.filter(booking_date=selected_date).values_list(
        "time_slot", flat=True
    )

    blocked_slots = BlockedTimeSlot.objects.filter(
        date=selected_date
    ).values_list("time_slot", flat=True)

    unavailable = set(booked_slots) | set(blocked_slots)

    available_slots = [
        {"value": value, "label": label}
        for value, label in all_slots
        if value not in unavailable
    ]

    return Response(
        {
            "is_bookable_day": True,
            "available_slots": available_slots,
        }
    )


# -------------------------
# CREATE BOOKING (DEBUG SAFE)
# -------------------------
@api_view(["POST"])
def create_booking(request):
    serializer = BookingSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Save booking FIRST (this is what we care about)
    booking = serializer.save()

    # -------------------------
    # 🚫 TEMPORARILY DISABLED
    # -------------------------

    # ❌ Owner email
    # try:
    #     send_owner_booking_email(booking)
    # except Exception as e:
    #     print("Owner email failed:", e)

    # ❌ Google Calendar
    # try:
    #     create_google_calendar_event(booking)
    # except Exception as e:
    #     print("Calendar failed:", e)

    # ❌ Customer confirmation email
    # if booking.email:
    #     try:
    #         send_mail(
    #             subject="Your booking is confirmed",
    #             message="Booking confirmed",
    #             from_email=settings.DEFAULT_FROM_EMAIL,
    #             recipient_list=[booking.email],
    #             fail_silently=False,
    #         )
    #     except Exception as email_error:
    #         print("Customer email failed:", email_error)

    # -------------------------
    # RETURN SUCCESS IMMEDIATELY
    # -------------------------
    return Response(
        {
            "message": "Booking created successfully.",
            "booking_id": booking.id,
        },
        status=status.HTTP_201_CREATED,
    )