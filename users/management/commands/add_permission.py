from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Добавить разрешение на удаление пользователей существующему администратору"""

    def handle(self, *args, **options):
        User = get_user_model()
        admin_email = "test@mail.ru"  # Замените на email вашего администратора

        try:
            admin_user = User.objects.get(email=admin_email)
            delete_permission = Permission.objects.get(codename="delete_user")

            admin_user.user_permissions.add(delete_permission)
            admin_user.save()

            self.stdout.write(
                self.style.SUCCESS(f"Разрешение на удаление пользователей добавлено пользователю {admin_email}.")
            )
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("Пользователь не найден."))
        except Permission.DoesNotExist:
            self.stdout.write(self.style.ERROR("Разрешение не найдено."))
