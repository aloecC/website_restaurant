from django.contrib.auth.models import User
from django.db import models

from users.models import CustomUser


class Halls(models.Model):
    """Модель зала в ресторане"""

    name = models.CharField(max_length=100, verbose_name="Название зала")
    description = models.TextField(blank=True, null=True, verbose_name="Описание зала")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Зал"
        verbose_name_plural = "Залы"


class Tables(models.Model):
    """Модель столиков в ресторане"""

    TABLES_CHOICES = [(i, str(i)) for i in range(1, 51)]

    number = models.IntegerField(unique=True, choices=TABLES_CHOICES, verbose_name="Номер стола")
    hall = models.ForeignKey(Halls, on_delete=models.PROTECT, related_name="tables", verbose_name="Зал")
    count_of_seats = models.PositiveSmallIntegerField(verbose_name="Количество сидячих мест")
    is_active = models.BooleanField(default=True, verbose_name="Статус столика")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Описание столика")

    def __str__(self):
        return f"Стол {self.number} ({self.hall.name})"

    class Meta:
        verbose_name = "Столик"
        verbose_name_plural = "Столики"
