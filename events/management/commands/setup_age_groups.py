from django.core.management.base import BaseCommand

from events.models import AgeGroup


class Command(BaseCommand):
    """Создает базовые возрастные группы"""

    def handle(self, *args, **options):
        groups = [
            {"name": "Дети (0-12 лет)", "from_age": 0, "before_age": 12, "code": "Children"},
            {"name": "Подростки (13-19 лет)", "from_age": 13, "before_age": 19, "code": "Teenagers"},
            {"name": "Молодежь (20-34 года)", "from_age": 20, "before_age": 34, "code": "Youth"},
            {"name": "Средний возраст (35-54 года)", "from_age": 35, "before_age": 54, "code": "Middle Age"},
            {"name": "Пожилые люди (55+)", "from_age": 55, "before_age": 150, "code": "Elderly"},
        ]

        for group in groups:
            obj, created = AgeGroup.objects.get_or_create(code=group["code"], defaults={"name": group["name"]})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Группа "{group["name"]}" создана'))
            else:
                self.stdout.write(f'Группа "{group["name"]}" уже существует')
