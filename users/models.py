from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class AgeGroup(models.Model):
    """Модель-справочник возрастных групп"""

    name = models.CharField(max_length=50, verbose_name="Возрастная группа")
    from_age = models.IntegerField(verbose_name="Возраст-порог")
    before_age = models.IntegerField(verbose_name="Возраст-потолок")
    code = models.CharField(max_length=20, unique=True, verbose_name="Код группы")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Возрастная группа"
        verbose_name_plural = "Возрастные группы"


class CustomUser(AbstractUser):
    """Кастомная модель пользователя"""

    GENDER_CHOICES = [
        ("man", "Мужчина"),
        ("woman", "Женщиина"),
    ]

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    gender = models.CharField(
        choices=GENDER_CHOICES, max_length=15, blank=True, null=True, help_text="Выберите ваш пол"
    )
    birth_date = models.DateField(verbose_name="Дата рождения", blank=True, null=True)

    email_confirmed = models.BooleanField(default=False)

    verification_code = models.CharField(max_length=6, blank=True, null=True)
    is_block = models.BooleanField(default=False)

    age_group = models.ForeignKey(AgeGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    def __str__(self):
        return self.email

    def calculate_age(self):
        """Высчитывает возраст пользователя"""
        if not self.birth_date:
            return None
        today = date.today()
        age = (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )
        return age


class TemporaryUser(models.Model):
    """Модель временного пользователя"""

    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    email = models.EmailField(unique=True, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    username = models.CharField(max_length=128, unique=True, null=True, blank=True)
    birth_date = models.DateField(verbose_name="Дата рождения", blank=True, null=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)
