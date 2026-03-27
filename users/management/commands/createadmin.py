from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.create(
            email="test@mail.ru",
            first_name="Admin",
            last_name="Admin",
        )

        user.set_password("1234")

        user.is_staff = True
        user.is_superuser = True

        user.save()

        self.stdout.write(self.style.SUCCESS("Администратор успешно создан"))

        # Получение разрешений
        delete_permission = Permission.objects.get(codename="delete_user")

        # Назначение разрешения пользователю
        user.user_permissions.add(delete_permission)

        self.stdout.write(self.style.SUCCESS("Администратор успешно создан с правами на удаление пользователей"))
