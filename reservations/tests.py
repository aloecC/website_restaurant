import datetime

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from reservations.models import Reservation
from reservations.views import ScoreTemplateView, ScoreViewTemplateView

User = get_user_model()


class ScoreViewsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user = User.objects.create_user(username="user1", password="pw", email="user1@example.test")

        def create_reservation(user, **kwargs):
            now = timezone.now()
            date = (now + datetime.timedelta(days=1)).date()
            start_time = datetime.time(12, 0)
            end_time = datetime.time(13, 0)

            defaults = {
                "user": user,
                "date": date,
                "start_time": start_time,
                "end_time": end_time,
                "status": kwargs.pop("status", "CONFIRMED"),
                "guests": kwargs.pop("guests", 1),
                "score": kwargs.pop("score", None),
                "comment_user": kwargs.pop("comment_user", ""),
                "comment_admin": kwargs.pop("comment_admin", ""),
            }
            defaults.update(kwargs)
            return Reservation.objects.create(**defaults)

        self.reservation = create_reservation(self.user)

    def test_score_template_view_get_includes_reservation_in_context(self):
        request = self.factory.get(f"/reservations/{self.reservation.pk}/score/")
        request.user = self.user

        view = ScoreTemplateView()
        view.request = request
        view.kwargs = {"pk": self.reservation.pk}

        ctx = view.get_context_data()
        self.assertIn("reservation_object", ctx)
        self.assertEqual(ctx["reservation_object"].pk, self.reservation.pk)

    def test_score_template_view_post_updates_reservation_and_redirects(self):
        request = self.factory.post(
            f"/reservations/{self.reservation.pk}/score/", data={"score": "5", "comment_user": "Отлично!"}
        )
        request.user = self.user

        view = ScoreTemplateView()
        view.request = request
        view.kwargs = {"pk": self.reservation.pk}

        response = view.post(request, pk=self.reservation.pk)

        self.assertIn(response.status_code, (302, 301), "Ожидался редирект после POST")

        self.reservation.refresh_from_db()
        self.assertEqual(str(self.reservation.score), "5")
        self.assertEqual(self.reservation.comment_user, "Отлично!")

    def test_score_view_template_view_context_contains_score_and_comments(self):
        self.reservation.score = "4"
        self.reservation.comment_user = "Хорошо"
        self.reservation.comment_admin = "Комментарий администратора"
        self.reservation.save()

        request = self.factory.get(f"/reservations/{self.reservation.pk}/score_show/")
        request.user = self.user

        view = ScoreViewTemplateView()
        view.request = request
        view.kwargs = {"pk": self.reservation.pk}

        view.object = view.get_object()

        ctx = view.get_context_data()
        self.assertEqual(ctx["score"], self.reservation.score)
        self.assertEqual(ctx["comment_user"], self.reservation.comment_user)
        self.assertEqual(ctx["comment_admin"], self.reservation.comment_admin)


class ReservationUpdateDeleteTests(TestCase):
    def setUp(self):

        self.staff = User.objects.create_user(username="staff", password="pw", is_staff=True, email="s@ex.com")
        self.owner = User.objects.create_user(username="owner", password="pw", is_staff=False, email="o@ex.com")
        self.other = User.objects.create_user(username="other", password="pw", is_staff=False, email="other@ex.com")

        def create_res(user, status="PENDING"):
            return Reservation.objects.create(
                user=user,
                date=(timezone.now() + datetime.timedelta(days=1)).date(),
                start_time=datetime.time(12, 0),
                end_time=datetime.time(13, 0),
                guests=2,
                status=status,
            )

        self.res_pending = create_res(self.owner, "PENDING")
        self.res_confirmed = create_res(self.owner, "CONFIRMED")
        self.res_completed = create_res(self.owner, "COMPLETED")

    def test_update_access_staff_can_access_any(self):
        self.client.force_login(self.staff)
        url = reverse("reservations:reservation_edit", kwargs={"pk": self.res_completed.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_access_owner_can_edit_pending_or_confirmed(self):
        self.client.force_login(self.owner)
        url_p = reverse("reservations:reservation_edit", kwargs={"pk": self.res_pending.pk})
        self.assertEqual(self.client.get(url_p).status_code, 200)
        url_c = reverse("reservations:reservation_edit", kwargs={"pk": self.res_confirmed.pk})
        self.assertEqual(self.client.get(url_c).status_code, 200)

    def test_update_access_owner_cannot_edit_completed(self):
        self.client.force_login(self.owner)
        url = reverse("reservations:reservation_edit", kwargs={"pk": self.res_completed.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_update_access_other_user_forbidden(self):
        self.client.force_login(self.other)
        url = reverse("reservations:reservation_edit", kwargs={"pk": self.res_pending.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_update_resets_status_to_pending(self):
        """Если статус был CONFIRMED, после сохранения он должен стать PENDING"""
        self.client.force_login(self.owner)
        url = reverse("reservations:reservation_edit", kwargs={"pk": self.res_confirmed.pk})

        data = {
            "date": self.res_confirmed.date,
            "start_time": self.res_confirmed.start_time,
            "end_time": self.res_confirmed.end_time,
            "guests": 5,
            "status": "CONFIRMED",
        }

        response = self.client.post(url, data)

        expected_url = reverse("reservations:reservation_detail", kwargs={"pk": self.res_confirmed.pk})
        self.assertRedirects(response, expected_url)

        self.res_confirmed.refresh_from_db()
        self.assertEqual(self.res_confirmed.status, "PENDING")
        self.assertEqual(self.res_confirmed.guests, 5)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("статус снова 'Ожидает подтверждения'" in str(m) for m in messages))

    def test_delete_access_staff_only(self):
        self.client.force_login(self.staff)
        url = reverse("reservations:reservation_delete", kwargs={"pk": self.res_pending.pk})
        self.assertEqual(self.client.get(url).status_code, 200)

        response = self.client.post(url)
        self.assertRedirects(response, reverse("reservations:reservation_list"))
        self.assertFalse(Reservation.objects.filter(pk=self.res_pending.pk).exists())

    def test_delete_access_owner_forbidden(self):
        self.client.force_login(self.owner)
        url = reverse("reservations:reservation_delete", kwargs={"pk": self.res_confirmed.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        response_post = self.client.post(url)
        self.assertEqual(response_post.status_code, 403)
        self.assertTrue(Reservation.objects.filter(pk=self.res_confirmed.pk).exists())
