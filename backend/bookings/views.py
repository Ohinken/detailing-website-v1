from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError

from .models import (
    Booking,
    WeeklyAvailability,
    ClosedDate,
    BlockedTimeSlot,
)
from .serializers import BookingSerializer


ALL_SLOTS = [
    {"value": "09:00-11:00", "label": "9:00 AM - 11:00 AM"},
    {"value": "11:30-01:30", "label": "11:30 AM - 1:30 PM"},
    {"value": "02:00-04:00", "label": "2:00 PM - 4:00 PM"},
]


def send_owner_booking_email(booking):
    subject = f"New booking: {booking.get_service_display()} on {booking.booking_date}"

    message = (
        f"New appointment booked for High Desert Auto Detail.\n\n"
        f"Customer Name: {booking.customer_name}\n"
        f"Phone: {booking.phone}\n"
        f"Email: {booking.email or 'Not provided'}\n"
        f"Vehicle: {booking.vehicle_make_model}\n"
        f"Detail Location: {booking.detail_location}\n"
        f"Service: {booking.get_service_display()}\n"
        f"Price: ${booking.service_price}\n"
        f"Date: {booking.booking_date}\n"
        f"Time: {booking.get_time_slot_display()}\n"
        f"Notes: {booking.notes or 'None'}\n"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.BUSINESS_NOTIFICATION_EMAIL],
        fail_silently=False,
    )


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

    booked_slots = Booking.objects.filter(booking_date=selected_date).values_list(
        "time_slot", flat=True
    )

    blocked_slots = BlockedTimeSlot.objects.filter(
        date=selected_date
    ).values_list("time_slot", flat=True)

    unavailable = set(booked_slots) | set(blocked_slots)

    available = [slot for slot in ALL_SLOTS if slot["value"] not in unavailable]

    return Response(
        {
            "is_bookable_day": True,
            "available_slots": available,
        }
    )


@api_view(["POST"])
def create_booking(request):
    serializer = BookingSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    try:
        booking = serializer.save()
    except IntegrityError:
        return Response(
            {"error": "That time slot is already booked."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if booking.email:
        subject = "Your High Desert Auto Detail booking is confirmed"
        message = (
            f"Hi {booking.customer_name},\n\n"
            f"Thanks for booking with High Desert Auto Detail.\n\n"
            f"Here are your appointment details:\n"
            f"Service: {booking.get_service_display()}\n"
            f"Date: {booking.booking_date}\n"
            f"Time: {booking.get_time_slot_display()}\n"
            f"Vehicle: {booking.vehicle_make_model}\n"
            f"Detail Location: {booking.detail_location}\n"
            f"Price: ${booking.service_price}\n\n"
            f"If you need to make any changes, please contact us.\n\n"
            f"High Desert Auto Detail\n"
            f"(505) 401-6071"
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.email],
                fail_silently=False,
            )
        except Exception as email_error:
            print(f"Customer confirmation email failed: {email_error}")

    try:
        send_owner_booking_email(booking)
    except Exception as owner_email_error:
        print(f"Owner booking email failed: {owner_email_error}")

    # Google Calendar still OFF for now
    # try:
    #     create_google_calendar_event(booking)
    # except Exception as calendar_error:
    #     print(f"Google Calendar event creation failed: {calendar_error}")

    return Response(
        {
            "message": "Booking created successfully.",
            "booking_id": booking.id,
        },
        status=status.HTTP_201_CREATED,
    )