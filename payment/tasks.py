import os
import time

import stripe
from celery import shared_task
from dotenv import load_dotenv
from borrowing.send_telegram_message import send_telegram_message
from payment.models import Payment

load_dotenv()


@shared_task
def check_session_for_expiration():
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

    payments = Payment.objects.filter(status=Payment.StatusChoices.PENDING)

    for payment in payments:
        session = stripe.checkout.Session.retrieve(payment.session_id)

        if session.expires_at and session.expires_at < int(time.time()):
            payment.status = Payment.StatusChoices.EXPIRED
            payment.save()
            message = f"Session {payment.session_id} is expired."
            send_telegram_message(message)
