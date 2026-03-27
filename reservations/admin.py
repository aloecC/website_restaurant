from django.contrib import admin

from reservations.models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (id, "guest_name", "guest_phone", "date", "table", "status", "guests")
    list_filter = ("table", "status", "date")
    search_fields = ("guest_phone", "guest_name", "guest_name", "guest_email")
