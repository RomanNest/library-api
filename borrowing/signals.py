from django.db.models.signals import post_save
from django.dispatch import receiver
from borrowing.models import Borrowing
from borrowing.send_telegram_message import send_telegram_message


@receiver(post_save, sender=Borrowing)
def notify_new_borrowing(sender, instance, created, **kwargs):
    if created:
        message = (f"Нова позика - Книга: {instance.book.title};"
                   f"Позичив: {instance.user.username};"
                   f"Дата повернення: {instance.expected_return}")
        send_telegram_message(message)
