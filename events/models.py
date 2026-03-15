from django.contrib.auth.models import User
from django.db import models

from restaurants.models import Hall
from users.models import CustomUser


class AgeGroup(models.Model):
    """Модель-справочник возрастных групп"""

    name = models.CharField(max_length=50, verbose_name="Возрастная группа")
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Возрастная группа"
        verbose_name_plural = "Возрастные группы"


class Events(models.Model):
    """Модель ананосов в ресторане"""

    name = models.CharField(max_length=100, verbose_name="Название")
    poster = models.ImageField(upload_to="events/", verbose_name="Постер", blank=True, null=True)
    hall = models.ManyToManyField(Hall, blank=True, verbose_name="Зал проведения")

    description = models.TextField(max_length=10000, verbose_name="Описание")
    price = models.PositiveIntegerField(default=0, blank=True, null=True)
    min_age = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name="Возрастное ограничение")

    date_start = models.DateTimeField(verbose_name="Дата начала", null=True)
    max_people = models.PositiveIntegerField(default=50, verbose_name="Макс. кол-во человек")

    recommend_audit_gender = models.CharField(
        choices=CustomUser.GENDER_CHOICES, max_length=15, blank=True, null=True, verbose_name="Целевой пол"
    )

    recommend_audit_ph_children = models.CharField(
        choices=CustomUser.CHILDREN_STATUS,
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Целевая аудитория (дети)",
    )

    recomend_audit_age = models.ManyToManyField(AgeGroup, blank=True, verbose_name="Целевые возрастные группы")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "мероприятие"
        verbose_name_plural = "мероприятия"
        ordering = ["-date_start"]
