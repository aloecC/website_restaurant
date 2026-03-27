import datetime
from urllib.parse import quote

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from events.forms import EventForm
from events.models import Event

User = get_user_model()


class DummyThread:
    """
    Замена threading.Thread, которая вызывает target синхронно при start().
    Это удобно для тестов: реальный фоновый поток не создаётся,
    а функция отправки писем выполняется сразу — мы можем проверить вызовы.
    """

    def __init__(self, target=None, args=(), kwargs=None, daemon=None):
        self._target = target
        self._args = args or ()
        self._kwargs = kwargs or {}

    def start(self):

        if self._target:
            self._target(*self._args, **self._kwargs)


class EventCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("events:event_create")

        self.staff_user = User.objects.create_user(
            username="staff_user",
            password="testpass",
            email="staff@example.com",
            is_staff=True,
        )

        self.recipient1 = User.objects.create_user(
            username="r1",
            password="pass",
            email="r1@example.com",
        )
        self.recipient1.email_confirmed = True
        self.recipient1.save()

        self.recipient2 = User.objects.create_user(
            username="r2",
            password="pass",
            email="r2@example.com",
        )
        self.recipient2.email_confirmed = True
        self.recipient2.save()

        self.not_confirmed = User.objects.create_user(
            username="r3",
            password="pass",
            email="r3@example.com",
        )
        self.not_confirmed.email_confirmed = False
        self.not_confirmed.save()

        self.form_data = {
            "name": "Тестовое событие",
            "description": "Описание события для теста.",
        }

    def test_get_as_staff_returns_200_and_uses_template(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/event_form.html")

    def test_non_staff_get_forbidden(self):
        non_staff = User.objects.create_user(username="plain", password="p", email="plain@example.com")
        self.client.force_login(non_staff)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)


class EventUpdateDeleteViewTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staff", email="u1@example.test", password="pw", is_staff=True
        )
        self.non_staff_user = User.objects.create_user(
            username="user", email="u2@example.test", password="pw", is_staff=False
        )

        self.event = Event.objects.create(
            name="Original name",
            date_start=timezone.now() + datetime.timedelta(days=1),
            is_archive=False,
        )

        self.update_url = reverse("events:event_edit", args=[self.event.pk])
        self.delete_url = reverse("events:event_delete", args=[self.event.pk])

    def test_update_get_as_staff_returns_200_and_uses_template(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/event_form.html")

        form = response.context.get("form")
        self.assertIsNotNone(form)
        self.assertEqual(form.instance.pk, self.event.pk)

    def test_update_non_staff_get_forbidden(self):
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 403)

    def test_update_unauthenticated_redirects_to_login(self):
        self.client.logout()
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 302)
        login_url = resolve_url(settings.LOGIN_URL)
        f"{login_url}?next={quote(self.update_url)}"
        self.assertIn(login_url, response["Location"])

    def test_delete_get_confirmation_as_staff_returns_200_and_context_has_event(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/events_confirm_delete.html")
        self.assertIn("event", response.context)
        self.assertEqual(response.context["event"].pk, self.event.pk)

    def test_delete_post_deletes_event_and_redirects(self):
        self.client.force_login(self.staff_user)
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)

        exists = Event.objects.filter(pk=self.event.pk).exists()
        self.assertFalse(exists)

    def test_delete_non_staff_forbidden(self):
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 403)

    def test_delete_unauthenticated_redirects_to_login(self):
        self.client.logout()
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 302)
        login_url = resolve_url(settings.LOGIN_URL)
        f"{login_url}?next={quote(self.delete_url)}"
        self.assertIn(login_url, response["Location"])
