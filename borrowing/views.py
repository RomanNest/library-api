from datetime import datetime

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer, BorrowingCreateSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("user", "book")

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingListSerializer

    @staticmethod
    def _params_to_inst(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        queryset = self.queryset
        is_active = self.request.query_params.get("is_active")
        user = self.request.user

        if user.is_staff:
            queryset = Borrowing.objects.all()
            user_id_param = self.request.query_params.get("user")

            if user_id_param:
                user_filter_id = self._params_to_inst(user_id_param)
                queryset = queryset.filter(user_id__in=user_filter_id)
        else:
            queryset = queryset.filter(user=user)

        if is_active:
            queryset = queryset.filter(actual_return__isnull=True)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user",
                type=OpenApiTypes.INT,
                description="Filter by user id, "
                            "allowed admins only (ex. ?user=1)",
            ),
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                description="Filter by active status "
                            "(ex. ?is_active=True)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(request=None)
    @action(detail=True, methods=["POST"], url_path="return")
    def return_borrowing(self, request, pk=None):
        borrowing = get_object_or_404(Borrowing, pk=pk)
        borrowing.actual_return = datetime.now()
        borrowing.book.inventory += 1
        borrowing.book.save()
        borrowing.save()

        return Response(
            {"detail": "Borrowing has returned"},
            status=status.HTTP_200_OK,
        )
