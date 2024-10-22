import stripe
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from payment.models import Payment
from payment.serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer,
)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_staff:
            queryset = queryset.filter(borrowing__user=self.request.user)
        if self.action in ["list", "retrieve"]:
            return queryset.select_related("borrowing")
        return queryset


class PaymentSuccessView(APIView):
    @extend_schema(
        summary="Get info about successful payment",
        description="Authenticated user can get info about successful payment"
    )
    def get(self, request, *args, **kwargs):
        session_id = request.query_params.get("session_id")
        payment = Payment.objects.get(session_id=session_id)

        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status == "paid":
            serializer = PaymentDetailSerializer(
                payment, data={"status": "PAID"}, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class PaymentCancelView(APIView):
    @extend_schema(
        summary="Get info about canceled payment",
        description="Authenticated user can get info about canceled payment"
    )
    def get(self, request, *args, **kwargs):
        return Response(
            {
                "status": "Payment cancelled. "
                          "Please, complete your payment within 24 hours"
            },
            status=status.HTTP_200_OK
        )
