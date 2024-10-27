from django.db.models.signals import post_save
from django.dispatch import receiver
from borrowing.models import Borrowing
from borrowing.send_telegram_message import send_telegram_message
from payment.stripe_session import create_stripe_session
from payment.models import Payment


@receiver(post_save, sender=Borrowing)
def notify_new_borrowing(sender, instance, created, **kwargs):
    if created:
        payment = create_stripe_session(instance)
        message = (f"Нова позика - Книга: {instance.book.title};"
                   f"Позичив: {instance.user.username};"
                   f"Дата повернення: {instance.expected_return}"
                   f"Вартість позики: {payment.money_to_pay} USD")
        send_telegram_message(message)
        create_stripe_session(instance)
