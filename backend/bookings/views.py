from datetime import datetime

import requests
from django.conf import settings
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


# 🔥 ADD YOUR LOGO URL HERE
LOGO_URL = "https://project-g5v34.vercel.app/emaillogo.png"


def send_mailgun_email(to_email, subject, text_message, html_message=None):
    data = {
        "from": f"High Desert Auto Detail <{settings.DEFAULT_FROM_EMAIL}>",
        "to": [to_email],
        "subject": subject,
        "text": text_message,
    }

    if html_message:
        data["html"] = html_message

    response = requests.post(
        f"{settings.MAILGUN_BASE_URL}/v3/{settings.MAILGUN_DOMAIN}/messages",
        auth=("api", settings.MAILGUN_API_KEY),
        data=data,
        timeout=20,
    )

    response.raise_for_status()
    return response


def build_email_html(title, booking):
    return f"""
    <div style="font-family: Arial, sans-serif; max-width:600px; margin:auto;">
        <h2 style="color:#111;">{title}</h2>

        <p><strong>Name:</strong> {booking.customer_name}</p>
        <p><strong>Phone:</strong> {booking.phone}</p>
        <p><strong>Email:</strong> {booking.email or 'Not provided'}</p>
        <p><strong>Vehicle:</strong> {booking.vehicle_make_model}</p>
        <p><strong>Location:</strong> {booking.detail_location}</p>
        <p><strong>Service:</strong> {booking.get_service_display()}</p>
        <p><strong>Price:</strong> ${booking.service_price}</p>
        <p><strong>Date:</strong> {booking.booking_date}</p>
        <p><strong>Time:</strong> {booking.get_time_slot_display()}</p>
        <p><strong>Notes:</strong> {booking.notes or 'None'}</p>

        <div style="text-align:center; margin-top:30px;">
            <img src="{LOGO_URL}" width="180" />
        </div>
    </div>
    """


def send_owner_booking_email(booking):
    subject = f"New booking: {booking.get_service_display()} on {booking.booking_date}"

    text_message = (
        f"New appointment booked.\n\n"
        f"{booking.customer_name} - {booking.get_time_slot_display()} on {booking.booking_date}"
    )

    html_message = build_email_html("New Booking Received", booking)

    return send_mailgun_email(
        to_email=settings.BUSINESS_NOTIFICATION_EMAIL,
        subject=subject,
        text_message=text_message,
        html_message=html_message,
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

    # ✅ CUSTOMER EMAIL
    if booking.email:
        subject = "Your High Desert Auto Detail booking is confirmed"

        text_message = f"""
        Hi {booking.customer_name},

        Your booking is confirmed!

        Date: {booking.booking_date}
        Time: {booking.get_time_slot_display()}
        """

        html_message = build_email_html("Booking Confirmed", booking)

        try:
            send_mailgun_email(
                to_email=booking.email,
                subject=subject,
                text_message=text_message,
                html_message=html_message,
            )
        except Exception as e:
            customer_email_error = str(e)
            print(f"Customer confirmation email failed: {e}")

    # ✅ OWNER EMAIL
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
        },
        status=status.HTTP_201_CREATED,
    )