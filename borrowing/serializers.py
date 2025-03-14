from rest_framework import serializers

from book.serializers import BookSerializer
from payment.serializers import PaymentListSerializer
from borrowing.models import Borrowing
from payment.models import Payment


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
    payment_info = PaymentListSerializer(
        many=True,
        read_only=True,
        source="payment",
    )

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
            "payment_info",
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
        )

    def validate(self, data):
        book = data.get("book")
        user = self.context["request"].user
        pending_payments = Payment.objects.filter(
            borrowing__user=user, status=Payment.StatusChoices.PENDING
        )

        if pending_payments.exists():
            raise serializers.ValidationError(
                "This borrowing is forbidden. "
                "You have to complete your pending payment"
            )
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


