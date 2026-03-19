from django.contrib.auth.models import User
from django.db import models


class Hall(models.Model):
    """Модель-справочник зала в ресторане"""

    name = models.CharField(max_length=100, verbose_name="Название зала")
    description = models.TextField(blank=True, null=True, verbose_name="Описание зала")
    is_active = models.BooleanField(default=True, verbose_name="Статус зала")
    capacity = models.PositiveIntegerField(default=0, verbose_name="Количество сидячих мест")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Зал"
        verbose_name_plural = "Залы"


class Table(models.Model):
    """Модель-справочник столиков в ресторане"""

    TABLES_CHOICES = [(i, str(i)) for i in range(1, 101)]

    number = models.IntegerField(unique=True, choices=TABLES_CHOICES, verbose_name="Номер стола")
    hall = models.ForeignKey(Hall, on_delete=models.PROTECT, related_name="tables", verbose_name="Зал")
    capacity = models.PositiveSmallIntegerField(verbose_name="Количество сидячих мест")
    is_active = models.BooleanField(default=True, verbose_name="Статус столика")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Описание столика")

    def __str__(self):
        return f"Стол {self.number}"

    class Meta:
        verbose_name = "Столик"
        verbose_name_plural = "Столики"
