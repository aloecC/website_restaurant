from django.contrib.auth.models import User
from django.db import models


class Table(models.Model):
    """Модель-справочник столиков в ресторане"""

    TABLES_CHOICES = [(i, str(i)) for i in range(1, 101)]

    number = models.IntegerField(unique=True, choices=TABLES_CHOICES, verbose_name="Номер стола")
    capacity = models.PositiveSmallIntegerField(verbose_name="Количество сидячих мест")
    is_active = models.BooleanField(default=True, verbose_name="Статус столика")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Описание столика")

    def __str__(self):
        return f"Стол {self.number}"

    class Meta:
        verbose_name = "Столик"
        verbose_name_plural = "Столики"


class TeamMember(models.Model):
    """Модель-справочник сотрудников в ресторане"""

    DEPARTMENTS_CHOICES = [
        ("Начальство", "Начальство"),
        ("Кухня", "Кухня"),
        ("Зал", "Зал"),
    ]

    POSITIONS_CHOICES = [
        ("Директор", "Директор"),
        ("Управляющий", "Управляющий"),
        ("Администратор", "Администратор"),
        # Кухня (Сердце "Берлоги")
        ("Шеф-повар", "Шеф-повар"),
        ("Су-шеф", "Су-шеф"),
        ("Мастер гриля", "Мастер гриля"),  # Важно для стейкхауса!
        ("Повар", "Повар"),
        ("Шеф-кондитер", "Шеф-кондитер"),  # Для ваших лесных десертов
        ("Метрдотель", "Метрдотель"),
        ("Сомелье", "Сомелье"),
        ("Старший официант", "Старший официант"),
        ("Официант", "Официант"),
        ("Бармен", "Бармен"),
        ("Хостес", "Хостес"),
    ]

    POSITION_TO_DEPARTMENT = {
        "Директор": "Начальство",
        "Управляющий": "Начальство",
        "Администратор": "Начальство",
        "Шеф-повар": "Кухня",
        "Су-шеф": "Кухня",
        "Мастер гриля": "Кухня",
        "Повар": "Кухня",
        "Шеф-кондитер": "Кухня",
        "Метрдотель": "Зал",
        "Сомелье": "Зал",
        "Старший официант": "Зал",
        "Официант": "Зал",
        "Бармен": "Зал",
        "Хостес": "Зал",
    }

    first_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Имя сотрудника")
    last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Имя сотрудника")
    position = models.CharField(choices=POSITIONS_CHOICES, max_length=40, verbose_name="Занимаемая должность")
    position_department = models.CharField(
        choices=DEPARTMENTS_CHOICES, max_length=40, verbose_name="Подразделение", blank=True, null=True
    )
    avatar = models.ImageField(upload_to="team_members/", blank=True, null=True)
    description = models.CharField(max_length=1255, blank=True, null=True, verbose_name="Описание сотрудника")
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return f"Сотрудник {self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def save(self, *args, **kwargs):
        if self.position and self.position in self.POSITION_TO_DEPARTMENT:
            self.position_department = self.POSITION_TO_DEPARTMENT[self.position]

        super().save(*args, **kwargs)
