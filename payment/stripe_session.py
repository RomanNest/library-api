import stripe
from django.conf import settings
from rest_framework.request import Request
from stripe.checkout import Session

from payment.models import Payment
from borrowing.models import Borrowing


stripe.api_key = settings.STRIPE_SECRET_KEY

FINE_MULTIPLIER = 2


def calculate_days_fee_amount(borrowing: Borrowing) -> int:
    days_fee = (
        borrowing.expected_return - borrowing.borrow_date
    ).days
    fee_per_day = borrowing.book.daily_fee
    return int(fee_per_day * days_fee * 100)


def calculate_days_of_overdue_amount(borrowing: Borrowing) -> int:
    days_of_overdue = (
        borrowing.actual_return - borrowing.borrow_date
    ).days
    daily_fee = borrowing.book.daily_fee
    return int(daily_fee * FINE_MULTIPLIER * days_of_overdue * 100)


def create_stripe_session(borrowing: Borrowing) -> Payment:
    book = borrowing.book

    if (
            borrowing.actual_return
            and borrowing.actual_return > borrowing.expected_return
    ):
        days_fee = calculate_days_fee_amount(borrowing)
        days_of_overdue = calculate_days_of_overdue_amount(borrowing)
        total_amount = days_fee + days_of_overdue
        name = (f"Payment for borrowing of {book.title} consists of"
                f"expected fee - {days_fee} and "
                f"overdue fee - {days_of_overdue}")
    else:
        total_amount = calculate_days_fee_amount(borrowing)
        name = f"Payment for borrowing of {book.title} is {total_amount}"

    success_url = settings.stripe_success_url
    cancel_url = settings.stripe_cancel_url

    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": total_amount,
                    "product_data": {
                        "name": name
                    },
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    # return session


# def create_stripe_payment_session(borrowing: Borrowing) -> Payment | None:
#     stripe_session = create_stripe_session(borrowing)

    payment = Payment.objects.create(
        status=Payment.StatusChoices.PENDING,
        borrowing=borrowing,
        session_id=session.id,
        session_url=session.url,
        money_to_pay=session.amount_total / 100,
        type=session.type,

    )

    return payment
