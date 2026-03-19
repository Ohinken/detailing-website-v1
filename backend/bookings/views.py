from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Booking, WeeklyAvailability, ClosedDate, BlockedTimeSlot
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
        return Response(
            {"error": "date query parameter is required, format YYYY-MM-DD"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response(
            {"error": "invalid date format, use YYYY-MM-DD"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    weekday = booking_date.weekday()

    weekly_rule = WeeklyAvailability.objects.filter(day_of_week=weekday).first()
    if not weekly_rule or not weekly_rule.is_bookable:
        return Response(
            {
                "date": date_str,
                "available_slots": [],
                "booked_slots": [],
                "blocked_slots": [],
                "is_bookable_day": False,
                "message": "This day is not available for booking.",
            }
        )

    if ClosedDate.objects.filter(date=booking_date).exists():
        return Response(
            {
                "date": date_str,
                "available_slots": [],
                "booked_slots": [],
                "blocked_slots": [],
                "is_bookable_day": False,
                "message": "This date is closed for booking.",
            }
        )

    booked_slots = set(
        Booking.objects.filter(booking_date=booking_date).values_list("time_slot", flat=True)
    )

    blocked_slots = set(
        BlockedTimeSlot.objects.filter(date=booking_date).values_list("time_slot", flat=True)
    )

    unavailable_slots = booked_slots | blocked_slots
    available = [slot for slot in ALL_SLOTS if slot["value"] not in unavailable_slots]

    return Response(
        {
            "date": date_str,
            "available_slots": available,
            "booked_slots": list(booked_slots),
            "blocked_slots": list(blocked_slots),
            "is_bookable_day": True,
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

    customer_email_error = None
    owner_email_error = None

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
        except Exception as e:
            customer_email_error = str(e)
            print(f"Customer confirmation email failed: {e}")

    try:
        send_owner_booking_email(booking)
    except Exception as e:
        owner_email_error = str(e)
        print(f"Owner booking email failed: {e}")

    return Response(
        {
            "message": "Booking created successfully.",
            "booking_id": booking.id,
            "customer_email_sent": customer_email_error is None,
            "owner_email_sent": owner_email_error is None,
            "customer_email_error": customer_email_error,
            "owner_email_error": owner_email_error,
        },
        status=status.HTTP_201_CREATED,
    )