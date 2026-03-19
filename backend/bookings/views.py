from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from google.oauth2 import service_account
from googleapiclient.discovery import build

from .models import Booking, WeeklyAvailability, ClosedDate, BlockedTimeSlot
from .serializers import BookingSerializer


ALL_SLOTS = [
    {"value": "09:00-11:00", "label": "9:00 AM - 11:00 AM"},
    {"value": "11:30-01:30", "label": "11:30 AM - 1:30 PM"},
    {"value": "02:00-04:00", "label": "2:00 PM - 4:00 PM"},
]


def get_slot_datetimes(booking):
    slot_map = {
        "09:00-11:00": ("09:00", "11:00"),
        "11:30-01:30": ("11:30", "13:30"),
        "02:00-04:00": ("14:00", "16:00"),
    }

    start_str, end_str = slot_map[booking.time_slot]

    start_dt = datetime.strptime(
        f"{booking.booking_date} {start_str}", "%Y-%m-%d %H:%M"
    )
    end_dt = datetime.strptime(
        f"{booking.booking_date} {end_str}", "%Y-%m-%d %H:%M"
    )

    return start_dt, end_dt


#def send_owner_booking_email(booking):
    #subject = f"New booking: {booking.get_service_display()} on {booking.booking_date}"

  #  message = (
        #f"New appointment booked for High Desert Auto Detail.\n\n"
        #f"Customer Name: {booking.customer_name}\n"
       # f"Phone: {booking.phone}\n"
       # f"Email: {booking.email or 'Not provided'}\n"
       # f"Vehicle: {booking.vehicle_make_model}\n"
        #f"Detail Location: {booking.detail_location}\n"
        #f"Service: {booking.get_service_display()}\n"
       # f"Price: ${booking.service_price}\n"
       # f"Date: {booking.booking_date}\n"
       # f"Time: {booking.get_time_slot_display()}\n"
       # f"Notes: {booking.notes or 'None'}\n"
 #   )

   # send_mail(
     #   subject=subject,
 #       message=message,
 #       from_email=settings.DEFAULT_FROM_EMAIL,
  #      recipient_list=[settings.BUSINESS_NOTIFICATION_EMAIL],
 #       fail_silently=False,
#    )


def create_google_calendar_event(booking):
    credentials = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/calendar"],
    )

    service = build("calendar", "v3", credentials=credentials)

    start_dt, end_dt = get_slot_datetimes(booking)

    event = {
        "summary": f"{booking.get_service_display()} - {booking.customer_name}",
        "location": booking.detail_location,
        "description": (
            f"Customer Name: {booking.customer_name}\n"
            f"Phone: {booking.phone}\n"
            f"Email: {booking.email or 'Not provided'}\n"
            f"Vehicle: {booking.vehicle_make_model}\n"
            f"Detail Location: {booking.detail_location}\n"
            f"Service: {booking.get_service_display()}\n"
            f"Price: ${booking.service_price}\n"
            f"Date: {booking.booking_date}\n"
            f"Time: {booking.get_time_slot_display()}\n"
            f"Notes: {booking.notes or 'None'}"
        ),
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": "America/Denver",
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "America/Denver",
        },
    }

    created_event = service.events().insert(
        calendarId=settings.GOOGLE_CALENDAR_ID,
        body=event,
    ).execute()

    booking.google_event_id = created_event.get("id")
    booking.save(update_fields=["google_event_id"])

    return created_event


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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    try:
        create_google_calendar_event(booking)
    except Exception as calendar_error:
        print(f"Google Calendar event creation failed: {calendar_error}")

    return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)