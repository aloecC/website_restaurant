from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse

from config import settings

from .models import TeamMember
from .views import ContactsTemplateView

User = get_user_model()


class RestaurantsViewTests(TransactionTestCase):

    def setUp(self):

        self.client = Client()
        self.contacts_url = reverse("restaurants:contacts")
        self.about_us_url = reverse("restaurants:about_us")

        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.force_login(self.user)

        self.team_member_boss = TeamMember.objects.create(
            first_name="Глава 1", position_department="Начальство", is_public=True
        )
        self.team_member_kitchen = TeamMember.objects.create(
            first_name="Шеф 1", position_department="Кухня", is_public=True
        )
        self.team_member_hall = TeamMember.objects.create(
            first_name="Официант 1", position_department="Зал", is_public=True
        )

    def test_contacts_page_GET_returns_200(self):
        response = self.client.get(self.contacts_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "restaurants/contacts.html")

    def test_contacts_page_POST_sends_email(self):

        form_data = {
            "name": "Тестовый Пользователь",
            "email": "test@example.com",
            "message": "Привет, это тестовое сообщение!",
        }

        with patch("restaurants.views.send_mail") as mock_send_mail:
            response = self.client.post(self.contacts_url, form_data)

        mock_send_mail.assert_called_once()

        expected_subject = "Поддержка"
        expected_message = 'Сообщение:"Привет, это тестовое сообщение!". Электронная почта для связи: test@example.com(Тестовый Пользователь).'
        expected_from_email = settings.DEFAULT_FROM_EMAIL
        expected_recipient_list = [settings.DEFAULT_FROM_EMAIL]

        mock_send_mail.assert_called_once_with(
            expected_subject, expected_message, expected_from_email, expected_recipient_list
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.contacts_url)

    def test_contacts_page_POST_redirects_on_success(self):

        form_data = {
            "name": "Другой Пользователь",
            "email": "other@example.com",
            "message": "Просто тест.",
        }
        with patch("restaurants.views.send_mail"):
            response = self.client.post(self.contacts_url, form_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.contacts_url)

    def test_about_us_page_GET_returns_200(self):
        response = self.client.get(self.about_us_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "restaurants/about_us.html")

    def test_about_us_page_context_data(self):
        response = self.client.get(self.about_us_url)

        self.assertIn("bosses", response.context)
        self.assertIn("team_kitchen", response.context)
        self.assertIn("team_hall", response.context)

        self.assertEqual(list(response.context["bosses"]), [self.team_member_boss])
        self.assertEqual(list(response.context["team_kitchen"]), [self.team_member_kitchen])
        self.assertEqual(list(response.context["team_hall"]), [self.team_member_hall])

        self.assertEqual(
            TeamMember.objects.filter(position_department="Начальство", is_public=False).count(), 0
        )  # Исключаем непубличных

    def test_show_menu_page_GET_returns_200(self):
        menu_url = reverse("restaurants:menu")
        response = self.client.get(menu_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "restaurants/menu.html")
