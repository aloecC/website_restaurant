import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from events.models import Event
from reservations.forms import ReservationForm
from reservations.models import Reservation
from restaurants.models import Table


class ReservationListView(LoginRequiredMixin, ListView):
    """Отображение списка броней"""

    model = Reservation
    template_name = "reservations/reservations.html"
    context_object_name = "reservations"

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.model.objects.all().order_by("-status", "date", "start_time")
        return self.model.objects.filter(user=user).order_by("-id")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        qs = self.get_queryset()

        context["pending"] = qs.filter(status="PENDING")
        context["confirmed"] = qs.filter(status="CONFIRMED")
        context["completed"] = qs.filter(status="COMPLETED")
        context["expired"] = qs.filter(status="EXPIRED")
        context["cancelled"] = qs.filter(status="CANCELLED")

        return context


class ReservationDetailView(LoginRequiredMixin, DetailView):
    """Подробное содержание брони"""

    model = Reservation
    template_name = "reservations/reservation_detail.html"
    context_object_name = "reservation"

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.model.objects.all()
        return self.model.objects.filter(user=user)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user
        new_status = request.POST.get("status")

        can_change = False

        if user.is_staff:
            can_change = True
        elif self.object.user == user and new_status == "CANCELLED":
            can_change = True

        if not can_change:
            messages.error(request, "У вас нет прав для этого действия.")
            return redirect(self.object.get_absolute_url())

        if new_status in dict(Reservation.STATUS_CHOICES).keys():
            if self.object.status != new_status:
                self.object.status = new_status
                self.object.save()

                if new_status == "CANCELLED":
                    messages.success(request, f"Бронирование №{self.object.pk} успешно отменено.")
                else:
                    messages.success(request, f"Статус брони изменен на '{self.object.get_status_display()}'.")
            else:
                messages.info(request, "Статус уже соответствует выбранному.")
        else:
            messages.error(request, "Некорректный статус.")

        return redirect(self.object.get_absolute_url())


class ReservationCreateView(CreateView):
    """Создание брони"""

    model = Reservation
    form_class = ReservationForm
    template_name = "reservations/reservation_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        event_id = self.request.GET.get("event_id")
        if event_id:
            kwargs["event"] = get_object_or_404(Event, pk=event_id)

        return kwargs

    def form_valid(self, form):
        session_data = form.cleaned_data
        session_data["date"] = session_data["date"].strftime("%Y-%m-%d")
        session_data["start_time"] = session_data["start_time"].strftime("%H:%M")
        session_data["end_time"] = session_data["end_time"].strftime("%H:%M")
        session_data["guests"] = session_data["guests"]

        self.request.session["booking_data"] = session_data
        return redirect("reservations:reservation_table_list")


class ReservationTableListView(ListView):
    """Выбор столика для бронирования"""

    model = Table
    template_name = "reservations/reservation_tables.html"
    context_object_name = "tables"

    def get_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.request.session.get("booking_data")

        if data:
            busy_tables_ids = Reservation.objects.filter(
                date=data["date"],
                start_time__lt=data["end_time"],
                end_time__gt=data["start_time"],
                status__in=["PENDING", "CONFIRMED"],
            ).values_list("table_id", flat=True)

            context["is_free"] = (
                Table.objects.filter(is_active=True, capacity__gte=data["guests"])
                .exclude(id__in=busy_tables_ids)
                .order_by("number")
            )

        return context

    def post(self, request, *args, **kwargs):
        table_id = request.POST.get("table_id")
        data = request.session.get("booking_data")

        if not (table_id and data):
            return redirect("reservations:reservation_create")

        try:
            table = Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            messages.error(request, "Выбранный стол не найден.")
            return redirect("reservations:reservation_create")

        booking_date = datetime.datetime.strptime(data["date"], "%Y-%m-%d").date()
        booking_start_time = datetime.datetime.strptime(data["start_time"], "%H:%M").time()
        booking_end_time = datetime.datetime.strptime(data["end_time"], "%H:%M").time()

        try:
            reservation = Reservation.objects.create(
                user=request.user if request.user.is_authenticated else None,
                table=table,
                date=booking_date,
                start_time=booking_start_time,
                end_time=booking_end_time,
                guests=data["guests"],
                guest_name=data["guest_name"],
                guest_phone=data["guest_phone"],
                status="PENDING",
            )

            del request.session["booking_data"]

            messages.success(request, f"Бронь №{reservation.pk} успешно создана.")
            return redirect("reservations:reservation_success")

        except Exception as e:
            print(f"Ошибка при создании бронирования: {e}")
            messages.error(request, f"Произошла ошибка при создании бронирования: {e}")
            return redirect("reservations:reservation_create")

            del request.session["booking_data"]
            return redirect("reservations:reservation_success")


class ReservationSuccessView(TemplateView):
    """Завершение бронирования"""

    template_name = "reservations/reservation_success.html"


class ReservationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Изменение брони"""

    model = Reservation
    form_class = ReservationForm
    template_name = "reservations/reservation_form.html"
    success_url = reverse_lazy("reservations:reservation_list")
    context_object_name = "reservation"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def test_func(self):

        reservation = self.get_object()
        user = self.request.user

        if user.is_staff:
            return True

        if reservation.user == user and reservation.status not in ["COMPLETED", "CANCELLED", "EXPIRED"]:
            return True

        return False

    def get_success_url(self):
        return reverse_lazy("reservations:reservation_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):

        reservation = form.save(commit=False)
        if reservation.status != "PENDING":
            reservation.status = "PENDING"
            messages.info(self.request, "Бронирование изменено. Его статус снова 'Ожидает подтверждения'.")

        reservation.save()

        return super().form_valid(form)


class ReservationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление брони"""

    model = Reservation
    template_name = "reservations/reservations_confirm_delete.html"
    success_url = reverse_lazy("reservations:reservation_list")

    def test_func(self):
        return self.request.user.is_staff


class ScoreTemplateView(LoginRequiredMixin, TemplateView):
    """Оставить оценку и написать отзыв о посещении"""

    template_name = "reservations/score.html"
    success_url = reverse_lazy("reservations:reservation_list")
    model = Reservation
    pk_url_kwarg = "pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get(self.pk_url_kwarg)

        reservation_object = Reservation.objects.get(pk=pk)
        context["reservation_object"] = reservation_object
        return context

    def post(self, request, *args, **kwargs):

        reservation_pk = kwargs.get("pk")
        score = request.POST.get("score")
        comment_user = request.POST.get("comment_user")
        reservation = Reservation.objects.get(pk=reservation_pk)

        reservation.score = score
        reservation.comment_user = comment_user
        reservation.save()

        return redirect(self.success_url)


class ScoreViewTemplateView(LoginRequiredMixin, DetailView):
    """Показывает оставленный отзыв на бронь"""

    template_name = "reservations/score_show.html"
    model = Reservation
    pk_url_kwarg = "pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservation = self.get_object()

        context["score"] = reservation.score
        context["comment_user"] = reservation.comment_user
        context["comment_admin"] = reservation.comment_admin

        return context
