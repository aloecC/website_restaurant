from django.core.management.base import BaseCommand

from events.models import AgeGroup


class Command(BaseCommand):
    """Создает базовые возрастные группы для мероприятий"""

    def handle(self, *args, **options):
        groups = [
            {"name": "Дети (0-12 лет)", "code": "Children"},
            {"name": "Подростки (13-19 лет)", "code": "Teenagers"},
            {"name": "Молодежь (20-34 года)", "code": "Youth"},
            {"name": "Средний возраст (35-54 года)", "code": "Middle Age"},
            {"name": "Пожилые люди (55+)", "code": "Elderly"},
        ]

        for group in groups:
            obj, created = AgeGroup.objects.get_or_create(code=group["code"], defaults={"name": group["name"]})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Группа "{group["name"]}" создана'))
            else:
                self.stdout.write(f'Группа "{group["name"]}" уже существует')
