import stripe
from django.conf import settings
from rest_framework.reverse import reverse

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

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
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
        success_url=(settings.BASE_URL
                     + reverse("payment:payment-success")
                     + "?session_id={CHECKOUT_SESSION_ID}"),
        cancel_url=settings.BASE_URL + reverse("payment:payment-cancel")

    )

    payment = Payment.objects.create(
        status=Payment.StatusChoices.PENDING,
        borrowing=borrowing,
        session_id=session.id,
        session_url=session.url,
        money_to_pay=session.amount_total / 100,
        type=Payment.TypeChoices.PAYMENT,

    )

    return payment
