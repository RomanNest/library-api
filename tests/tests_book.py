from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from rest_framework import status

from book.models import Book
from book.serializers import BookListSerializer

BOOKS_URL = reverse("books:book-list")


def detail_url(book_id: int) -> str:
    return reverse("books:book-detail", args=[book_id])


def sample_book(**params):
    defaults = {
        "title": "Test Book",
        "author": "Test Author",
        "cover": Book.CoverChoices.HARD,
        "inventory": 3,
        "daily_fee": 1.5,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


class UnauthenticatedBookApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.book = sample_book()

    def test_unauthenticated_book_list(self) -> None:
        res = self.client.get(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_created_book_forbidden(self) -> None:
        payload = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": Book.CoverChoices.HARD,
            "inventory": 3,
            "daily_fee": 1.5,
        }
        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword",
            is_staff=False,
        )
        self.client.force_authenticate(user=self.user)
        self.book = sample_book()

    def test_created_book_forbidden(self) -> None:
        payload = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "Test Cover",
            "inventory": 3,
            "daily_fee": 1.5,
        }
        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_books(self) -> None:
        res = self.client.get(BOOKS_URL)
        books = Book.objects.all()
        serializer = BookListSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_delete_book_forbidden(self) -> None:
        res = self.client.delete(detail_url(self.book.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)
        self.book = sample_book()

    def test_created_book(self) -> None:
        payload = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": Book.CoverChoices.HARD,
            "inventory": 3,
            "daily_fee": 1.5,
        }
        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.all().count(), 2)

    def test_auth_delete_book(self) -> None:
        res = self.client.delete(detail_url(self.book.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.all().count(), 0)
