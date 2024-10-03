from rest_framework import serializers

from book.serializers import BookSerializer
from borrowing.models import Borrowing


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.CharField(source="book.title", read_only=True)
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "user",
            "is_active",
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=False, read_only=True)
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return",
            "actual_return",
            "actual_return",
            "book",
            "user",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return",
            "actual_return",
            "book",
            "user",
        )

    def validate(self, data):
        book = data.get("book")
        if book.inventory == 0:
            raise serializers.ValidationError("There isn't available book")
        return data

    def create(self, validated_data):
        book = validated_data.get("book")
        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.create(
            user=self.context["request"].user,
            **validated_data,
        )

        return borrowing


