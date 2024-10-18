from rest_framework import serializers

from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        )


class PaymentListSerializer(PaymentSerializer):
    borrowing = serializers.CharField(source="borrowing.id", read_only=True)
    user = serializers.CharField(
        source="borrowing.user.email",
        read_only=True,
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "borrowing",
            "status",
            "session_url",
            "session_id",
            "money_to_pay",
        )


class PaymentDetailSerializer(PaymentSerializer):
    borrowing = serializers.CharField(source="borrowing", read_only=True)
    user = serializers.CharField(
        source="borrowing.user.email",
        read_only=True,
    )

    class Meta:
        model = Payment
        fields = (
            "user",
            "status",
            "type",
            "money_to_pay",
            "session_url",
            "session_id",
            "borrowing",
        )
