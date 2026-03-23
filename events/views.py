import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from config.settings import DEFAULT_FROM_EMAIL

from .forms import EventForm
from .models import Event


class EventActualListView(ListView):
    """Отображение списка скорых мероприятий"""

    model = Event
    template_name = "events/home.html"
    context_object_name = "event_actual_list"

    def get_queryset(self):
        events = cache.get("events_ctual_queryset")
        if events is None:
            now = datetime.datetime.now()
            seven_days_from_now = now + datetime.timedelta(days=7)

            events = self.model.objects.filter(date_start__gte=now, date_start__lte=seven_days_from_now).order_by(
                "date_start"
            )

            cache.set("events_ctual_queryset", events, 60 * 15)

        return events


class EventListView(ListView):
    """Отображение списка всех мероприятий"""

    model = Event
    template_name = "events/events.html"
    context_object_name = "events"

    def get_queryset(self):
        return self.model.objects.filter(is_archive=False).order_by("date_start")

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


class EventCreateView(CreateView):
    """Создание мероприятия"""

    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:events_list")


class EventUpdateView(UpdateView):
    """Изменение мероприятия"""

    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:events_list")


class EventDeleteView(DeleteView):
    """Удаление мероприятия"""

    model = Event
    template_name = "events/events_confirm_delete.html"
    success_url = reverse_lazy("events:events_list")
