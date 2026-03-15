from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель пользователя"""

    GENDER_CHOICES = [
        ("man", "Мужчина"),
        ("woman", "Женщиина"),
    ]

    CHILDREN_STATUS = [
        ("Yes", "Есть дети"),
        ("No", "Нет детей"),
    ]

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    gender = models.CharField(
        choices=GENDER_CHOICES, max_length=15, blank=True, null=True, help_text="Выберите ваш пол"
    )
    pr_children = models.CharField(
        choices=CHILDREN_STATUS, max_length=15, blank=True, null=True, help_text="Обозначьте наличие детей"
    )
    age = models.PositiveSmallIntegerField(max_length=3, blank=True, null=True, help_text="Введите ваш возраст")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    def __str__(self):
        return self.email
