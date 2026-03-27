import datetime
import threading

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.core.mail import EmailMessage, send_mail
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from config.settings import DEFAULT_FROM_EMAIL
from reservations.models import Reservation
from users.models import CustomUser

from .forms import EventForm
from .models import Event


class EventActualListView(ListView):
    """Отображение списка скорых мероприятий"""

    model = Event
    template_name = "events/home.html"
    context_object_name = "event_actual_list"

    def get_queryset(self):
        events = cache.get("events_actual_queryset")
        if events is None:
            now = datetime.datetime.now()
            seven_days_from_now = now + datetime.timedelta(days=7)

            events = self.model.objects.filter(date_start__gte=now, date_start__lte=seven_days_from_now).order_by(
                "date_start"
            )

            cache.set("events_actual_queryset", events, 60 * 15)

        return events


class EventListView(ListView):
    """Отображение списка всех мероприятий"""

    model = Event
    template_name = "events/events.html"
    context_object_name = "events"

    def get_queryset(self):
        events = cache.get("events_queryset")
        if events is None:
            events = self.model.objects.filter(is_archive=False).order_by("date_start")
            cache.set("events_queryset", events, 60 * 15)
        return events

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["is_moderator"] = user.is_staff or user.groups.filter(name="Модератор").exists()
        context["events_archive"] = self.model.objects.filter(is_archive=True)
        return context


class EventDetailView(DetailView):
    """Подробное содержание мероприятия"""

    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        context["is_moderator"] = user.is_staff and user.groups.filter(name="Модератор").exists()

        return context


class EventCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Создание мероприятия"""

    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:events_list")

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):

        response = super().form_valid(form)
        recipients = list(
            CustomUser.objects.filter(email_confirmed=True)
            .exclude(email__isnull=True)
            .exclude(email__exact="")
            .values_list("email", flat=True)
        )

        if recipients:
            subject = f"Приглашение: {self.object.name}"
            event_url = self.request.build_absolute_uri(
                getattr(self.object, "get_absolute_url", lambda: reverse_lazy("events:events_list"))()
            )
            message = (
                f"Здравствуйте!\n\n"
                f"Приглашаем вас на мероприятие: {self.object.name}\n\n"
                f"{(self.object.description or '')}\n\n"
                f"Ссылка: {event_url}\n\n"
                f"С уважением,\n{getattr(settings, 'SITE_NAME', 'Сервис')}"
            )
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")

            threading.Thread(
                target=self._send_email_bcc,
                args=(subject, message, from_email, recipients),
                daemon=True,
            ).start()

        return response

    def _send_email_bcc(self, subject, message, from_email, recipients):
        try:
            email = EmailMessage(subject=subject, body=message, from_email=from_email, to=[], bcc=recipients)
            email.send(fail_silently=False)
        except Exception:
            import logging

            logging.exception("Ошибка при отправке приглашений на событие")


class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Изменение мероприятия"""

    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:events_list")

    def test_func(self):
        return self.request.user.is_staff


class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление мероприятия"""

    model = Event
    template_name = "events/events_confirm_delete.html"
    success_url = reverse_lazy("events:events_list")
    context_object_name = "event"

    def test_func(self):
        return self.request.user.is_staff


class ShowReservationEventDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Просмотр броней в день определенного мероприятия"""

    model = Event
    template_name = "events/reservs_event_list.html"
    context_object_name = "reservs_event"

    def get_reservation_gor_event(self):
        event = self.object
        date_event = event.date_start.date()
        time_event_start = event.date_start.time()
        qs = Reservation.objects.filter(date=date_event).order_by("-status")
        return qs.exclude(end_time__lt=time_event_start)

    def test_func(self):
        return self.request.user.is_staff

    def get_count(self):
        reservs = self.get_reservation_gor_event()
        count = 0
        for reserv in reservs:
            if reserv.status != "CANCALLED":
                count += 1
        return count

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        qs = self.get_reservation_gor_event()
        context["pending"] = qs.filter(status="PENDING")
        context["confirmed"] = qs.filter(status="CONFIRMED")

        context["in_event"] = self.get_reservation_gor_event()

        context["count"] = self.get_count()

        return context
