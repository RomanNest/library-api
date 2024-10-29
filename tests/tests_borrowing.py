from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from rest_framework import status

from book.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)
from payment.models import Payment

BORROWING_URL = reverse("borrowing:borrowing-list")


def detail_url(book_id: int) -> str:
    return reverse("borrowing:borrowing-detail", args=[book_id])


def sample_book(**params):
    defaults = {
        "title": "Test Book",
        "author": "Test Author",
        "cover": Book.CoverChoices.HARD,
        "inventory": 6,
        "daily_fee": 2,
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


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword",
            is_staff=False,
        )
        self.user_1 = get_user_model().objects.create_user(
            email="test_1@test.com",
            password="testpassword",
            is_staff=False,
        )
        self.client.force_authenticate(user=self.user)

        self.book = sample_book()
        self.book_1 = sample_book(title="Test_1 Book")

        self.borrowing = sample_borrowing(user=self.user, book=self.book)
        self.borrowing_1 = sample_borrowing(user=self.user_1, book=self.book_1)

    def test_borrowing_list(self) -> None:
        res = self.client.get(BORROWING_URL)
        borrowings = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingListSerializer(borrowings, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), borrowings.count())

    def test_borrowing_detail(self) -> None:
        res = self.client.get(detail_url(self.borrowing.id))
        serializer = BorrowingDetailSerializer(self.borrowing)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_borrowing_create(self) -> None:
        Payment.objects.filter(borrowing__user=self.user).update(status="PAID")
        payload = {
            "borrow_date": datetime.now().date(),
            "expected_return": datetime.now().date() + timedelta(days=10),
            "book": self.book.id,
            "user": self.user.id,
        }
        res = self.client.post(BORROWING_URL, payload)

        self.book.inventory -= 1
        self.book.save()
        self.book.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.book.inventory, 5)

    def test_borrowing_create_nor_allowed_if_previous_not_paid(self) -> None:
        payload = {
            "borrow_date": datetime.now().date(),
            "expected_return": datetime.now().date() + timedelta(days=10),
            "book": self.book.id,
            "user": self.user.id,
        }
        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_borrowing_create_forbidden_forbidden_if_inventory_is_zero(self) -> None:
        book = sample_book(inventory=0)
        Payment.objects.filter(borrowing__user=self.user).update(status="PAID")
        payload = {
            "borrow_date": datetime.now().date(),
            "expected_return": datetime.now().date() + timedelta(days=10),
            "book": book.id,
            "user": self.user.id,
        }
        res = self.client.post(BORROWING_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_book(self) -> None:
        borrowing = sample_borrowing(user=self.user)
        url = detail_url(borrowing.id) + "return/"
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["detail"], "Borrowing has returned")

    def test_checking_if_book_is_returned(self) -> None:
        borrowing = sample_borrowing(
            user=self.user,
            actual_return=datetime.now().date(),
        )
        url = detail_url(borrowing.id) + "return/"
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["detail"], "Your borrowing is already returned")


class AdminBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword",
            is_staff=True,
        )
        self.user_1 = get_user_model().objects.create_user(
            email="test1@test.com",
            password="testpassword",
            is_staff=False,
        )
        self.client.force_authenticate(user=self.user)

        self.book = sample_book()
        self.book_1 = sample_book(title="Test_1 Book")

        self.borrowing = sample_borrowing(user=self.user, book=self.book)
        self.borrowing_1 = sample_borrowing(user=self.user_1, book=self.book_1)

    def test_list_all_borrowing(self) -> None:
        res = self.client.get(BORROWING_URL)
        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_borrowing_detail_another_user(self) -> None:
        res = self.client.get(detail_url(self.borrowing_1.id))
        serializer = BorrowingDetailSerializer(self.borrowing_1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
