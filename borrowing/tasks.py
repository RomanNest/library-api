from datetime import date
from celery import shared_task

from borrowing.models import Borrowing
from borrowing.send_telegram_message import send_telegram_message


@shared_task
def check_overdue_borrowings():
    today = date.today()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return__lte=today,
        actual_return__isnull=True,
    )
    if overdue_borrowings:
        for borrowing in overdue_borrowings:
            message = (f"Overdue borrowing - book: {borrowing.book.title},"
                       f"must be returned: {borrowing.expected_return}.")
            send_telegram_message(message)
        else:
            send_telegram_message("No overdue borrowing today.")
