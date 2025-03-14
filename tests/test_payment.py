from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import stripe
from django.contrib.auth import get_user_model

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from book.models import Book
from payment.models import Payment
from borrowing.models import Borrowing
from payment.serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer,
)

PAYMENT_URL = reverse("payment:payment-list")


def sample_book(**params):
    defaults = {
        "title": "Test Book",
        "author": "Test Author",
        "cover": "Test Cover",
        "inventory": 3,
        "daily_fee": 1.5,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def sample_borrowing(**params):
    book = sample_book()
    user = params.get("user")
    defaults = {
        "borrow_date": datetime.now().date(),
        "expected_return": datetime.now().date() + timedelta(days=10),
        "book": book,
        "user": user,
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


def sample_payment(**params):
    borrowing = sample_borrowing()
    defaults = {
        "borrowing": borrowing,
    }
    defaults.update(params)

    return Payment.objects.create(**defaults)


class UnauthenticatedPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test__auth_required(self):
        res = self.client.get(PAYMENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_1 = get_user_model().objects.create_user(
            "test1@test.com",
            "password_test",
        )
        self.user_2 = get_user_model().objects.create_user(
            "test2@test.com",
            "password_test",
        )
        self.client.force_authenticate(user=self.user_1)

        self.book = sample_book()
        self.book_1 = sample_book(title="Sample Book")

        self.borrowing = sample_borrowing(user=self.user_1)
        self.borrowing_1 = sample_borrowing(
            book=self.book_1,
            user=self.user_2,
        )

    def test_user_can_see_only_own_payments(self):
        payments = Payment.objects.filter(borrowing__user=self.user_1)
        res = self.client.get(PAYMENT_URL)
        serializer = PaymentListSerializer(payments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), payments.count())
