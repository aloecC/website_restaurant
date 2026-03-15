import datetime
from datetime import time, timedelta

from django import forms
from django.utils import timezone

from .models import Halls, Reservation, Tables

RESTAURANT_OPEN_TIME = time(11, 0, 0)
RESTAURANT_CLOSE_TIME = time(0, 0, 0)  # 00:00 (полуночь)
MAX_RESERVATION_DURATION = timedelta(hours=3)  # Максимальная длительность брони


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["table", "date", "start_time", "end_time", "guests", "guest_name", "guest_phone"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean_end_time(self):
        start_time = self.cleaned_data.get("start_time")
        end_time = self.cleaned_data.get("end_time")

        if start_time and end_time and end_time <= start_time:
            raise forms.ValidationError("Время окончания должно быть позже времени начала.")

        return end_time

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        date = cleaned_data.get("date")

        if not (start_time and end_time and date):
            return cleaned_data

        if start_time < RESTAURANT_OPEN_TIME or end_time > RESTAURANT_CLOSE_TIME:

            is_within_working_hours = False

        else:
            is_within_working_hours = True

        if not is_within_working_hours:
            raise forms.ValidationError(
                f"Ресторан работает с {RESTAURANT_OPEN_TIME.strftime('%H:%M')} до {RESTAURANT_CLOSE_TIME.strftime('%H:%M')}. "
                f"Выберите время в рамках рабочего дня."
            )

        if date:
            dt_start = timezone.make_aware(datetime.combine(date, start_time))
            dt_end = timezone.make_aware(datetime.combine(date, end_time))

            if dt_end < dt_start:
                dt_end += timedelta(days=1)

            reservation_duration = dt_end - dt_start

            if reservation_duration > MAX_RESERVATION_DURATION:
                raise forms.ValidationError(
                    f"Максимальная длительность бронирования: {MAX_RESERVATION_DURATION.total_seconds() // 3600} часа."
                )

        return cleaned_data
