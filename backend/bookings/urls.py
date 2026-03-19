from django.urls import path
from .views import available_slots, create_booking

urlpatterns = [
    path("available-slots/", available_slots, name="available-slots"),
    path("create/", create_booking, name="create-booking"),
]