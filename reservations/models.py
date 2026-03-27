from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from restaurants.models import Table
from users.models import CustomUser


class Reservation(models.Model):
    """Модель бронирования столиков"""

    STATUS_CHOICES = [
        ("PENDING", "Ожидает подтверждения"),  # Временная блокировка (15 минут)
        ("CONFIRMED", "Подтверждена"),  # Бронь подтверждена
        ("CANCELLED", "Отменена"),  # Бронь отменена пользователем или системой
        ("EXPIRED", "Просрочена"),  # PENDING бронь истекла по времени (более явный статус, чем CANCELLED)
        ("COMPLETED", "Завершена"),  # Посещение состоялось
    ]

    SCORE_CHOICES = [
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь"
    )
    guest_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Имя гостя")
    guest_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон гостя")
    guest_email = models.EmailField(blank=True, null=True, verbose_name="Email гостя")
    table = models.ForeignKey(Table, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Столик")
    date = models.DateField(verbose_name="Дата бронирования")
    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время окончания")

    reminder_sent = models.BooleanField(default=False)
    guests = models.PositiveSmallIntegerField(verbose_name="Количество гостей")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="PENDING", verbose_name="Статус бронирования"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время последнего изменения")

    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Время истечения временной брони")

    score = models.CharField(
        max_length=20, choices=SCORE_CHOICES, null=True, blank=True, verbose_name="Оценка посещения"
    )

    comment_user = models.CharField(max_length=3000, null=True, blank=True, verbose_name="Комментарий пользователя")

    comment_admin = models.CharField(max_length=3000, null=True, blank=True, verbose_name="Обратная связь по брони")

    def __str__(self):
        return f"Бронь {self.table.number} на {self.date} {self.start_time}-{self.end_time} ({self.status})"

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["date", "start_time"]

    def get_absolute_url(self):
        return reverse("reservations:reservation_detail", args=[str(self.pk)])
