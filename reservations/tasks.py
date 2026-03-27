import datetime
import logging
from datetime import timedelta

from celery import shared_task
from celery.schedules import crontab
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F, Q
from django.db.models.functions import ExtractHour, ExtractMinute
from django.utils import timezone

from .models import Reservation

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def delete_old_cancelled_reservations(self):
    """Удаляет бронирования со статусом 'CANCELLED', которые были созданы более 30 дней назад."""
    days_threshold = 30

    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_threshold)

    old_cancelled_reservations = Reservation.objects.filter(status="CANCELLED", created_at__lt=cutoff_date)

    count = old_cancelled_reservations.count()

    if count > 0:
        deleted_count, _ = old_cancelled_reservations.delete()
        print(f"Удалено {deleted_count} старых отмененных бронирований (старше {days_threshold} дней).")
    else:
        print(f"Нет старых отмененных бронирований для удаления (старше {days_threshold} дней).")

    return count


@shared_task(bind=True)
def update_reservation_statuses(self):
    """Обновляет статусы бронирований:
    'CONFIRMED' -> 'COMPLETED', если время окончания брони прошло.
    'PENDING' -> 'EXPIRED', если время окончания брони прошло и статус не был изменен."""
    try:
        now = timezone.localtime(timezone.now())
        confirmed_reservations = Reservation.objects.filter(status="CONFIRMED")

        confirmed_to_complete_pks = []
        for res in confirmed_reservations.only("pk", "end_time", "date"):
            if res.end_time and res.date:
                end_dt = (
                    timezone.make_aware(datetime.combine(res.date, res.end_time))
                    if timezone.is_naive(datetime.combine(res.date, res.end_time))
                    else datetime.combine(res.date, res.end_time)
                )
                if end_dt <= now:
                    confirmed_to_complete_pks.append(res.pk)

        if confirmed_to_complete_pks:
            updated_count_completed, _ = Reservation.objects.filter(pk__in=confirmed_to_complete_pks).update(
                status="COMPLETED"
            )
            logger.info("Updated %d CONFIRMED reservations to COMPLETED.", updated_count_completed)
        else:
            logger.info("No CONFIRMED reservations to update to COMPLETED.")

        pending_reservations = Reservation.objects.filter(status="PENDING")
        pending_to_expire_pks = []
        for res in pending_reservations.only("pk", "end_time", "date"):
            if res.end_time and res.date:
                end_dt = (
                    timezone.make_aware(datetime.combine(res.date, res.end_time))
                    if timezone.is_naive(datetime.combine(res.date, res.end_time))
                    else datetime.combine(res.date, res.end_time)
                )
                if end_dt <= now:
                    pending_to_expire_pks.append(res.pk)

        if pending_to_expire_pks:
            updated_count_expired, _ = Reservation.objects.filter(pk__in=pending_to_expire_pks).update(
                status="EXPIRED"
            )
            logger.info("Updated %d PENDING reservations to EXPIRED.", updated_count_expired)
        else:
            logger.info("No PENDING reservations to update to EXPIRED.")

        return True

    except Exception as e:
        logger.exception("Error updating reservation statuses: %s", e)
        raise e


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_reservation_reminder(self):
    """Отправляет напоминание по email за 1 час до старта брони."""
    try:
        now = timezone.localtime(timezone.now())
        target_dt = now + timedelta(hours=1)

        target_date = target_dt.date()
        target_hour = target_dt.hour
        target_minute = target_dt.minute

        qs = (
            Reservation.objects.annotate(
                start_hour=ExtractHour("start_time"),
                start_minute=ExtractMinute("start_time"),
            )
            .filter(
                date=target_date,
                start_hour=target_hour,
                start_minute=target_minute,
                status="CONFIRMED",
                reminder_sent=False,
            )
            .select_related("user")
        )

        if not qs.exists():
            logger.info("No reservations to remind at %s", target_dt)
            return "No reservations to remind."

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")
        sent_count = 0

        for reservation in qs:
            try:
                recipient = None
                if getattr(reservation, "guest_email", None):
                    recipient = reservation.guest_email
                elif getattr(reservation, "user", None) and getattr(reservation.user, "email", None):
                    recipient = reservation.user.email

                if not recipient:
                    logger.warning("Reservation %s has no email, skipping", reservation.pk)
                    continue

                subj_title = "Бронирование"
                if hasattr(reservation, "event") and reservation.event:
                    subj_title = getattr(reservation.event, "name", getattr(reservation.event, "title", subj_title))

                subject = f"Напоминание: бронирование через 1 час — {subj_title}"
                start_time_str = reservation.start_time.strftime("%H:%M") if reservation.start_time else "время"
                body_lines = [
                    "Здравствуйте!",
                    "",
                    f"Напоминаем: у вас бронирование на {reservation.date} в {start_time_str}.",
                    "",
                    "Если вы не собираетесь приходить, пожалуйста отмените бронь.",
                ]
                body = "\n".join(body_lines)

                send_mail(subject, body, from_email, [recipient], fail_silently=False)

                with transaction.atomic():
                    reservation.reminder_sent = True
                    reservation.save(update_fields=["reminder_sent"])

                sent_count += 1
                logger.info("Reminder sent for reservation %s to %s", reservation.pk, recipient)

            except Exception as e:
                logger.exception("Failed to send reminder for reservation %s: %s", reservation.pk, e)
                continue

        return f"Sent reminders: {sent_count}"

    except Exception as exc:
        logger.exception("send_reservation_reminder failed: %s", exc)
        raise self.retry(exc=exc)
