from datetime import datetime, time, timedelta

from django import forms
from django.utils import timezone

from .models import Reservation

RESTAURANT_OPEN_TIME = time(11, 0, 0)
RESTAURANT_CLOSE_TIME = time(00, 0, 0)
MAX_RESERVATION_DURATION = timedelta(hours=5)


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["date", "start_time", "end_time", "guests", "guest_name", "guest_phone"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "start_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "end_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "guests": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Кол-во гостей"}),
            "guest_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ваше имя"}),
            "guest_phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ваш телефон"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        event = kwargs.pop("event", None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.fields["guest_name"].initial = user.first_name if user.first_name else user.username
            self.fields["guest_name"].widget.attrs["readonly"] = True
            if user.phone_number:
                self.fields["guest_phone"].initial = getattr(user, "phone_number", "")
                self.fields["guest_phone"].widget.attrs["readonly"] = True

        if event:
            self.fields["date"].initial = event.date_start.date()
            self.fields["start_time"].initial = event.date_start.time()

            self.fields["date"].widget.attrs["readonly"] = True
            self.fields["start_time"].widget.attrs["readonly"] = True

            self.fields["date"].help_text = f"Бронирование на мероприятие: {event.name}"

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

        is_after_open = start_time >= RESTAURANT_OPEN_TIME

        if RESTAURANT_CLOSE_TIME == time(0, 0):

            is_before_close = True
        else:
            is_before_close = end_time <= RESTAURANT_CLOSE_TIME

        if not (is_after_open and is_before_close):
            raise forms.ValidationError(
                f"Ресторан работает с {RESTAURANT_OPEN_TIME.strftime('%H:%M')} "
                f"до {RESTAURANT_CLOSE_TIME.strftime('%H:%M')}. "
                "Выберите время в рамках рабочего дня."
            )

        dt_start = timezone.make_aware(datetime.combine(date, start_time))
        dt_end = timezone.make_aware(datetime.combine(date, end_time))

        if dt_end <= dt_start:

            dt_end += timedelta(days=1)

        reservation_duration = dt_end - dt_start
        if reservation_duration > MAX_RESERVATION_DURATION:
            raise forms.ValidationError(
                f"Максимальная длительность бронирования: {MAX_RESERVATION_DURATION.total_seconds() // 3600} часа."
            )
        return cleaned_data
