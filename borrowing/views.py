from django.shortcuts import render
from rest_framework import viewsets

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer, BorrowingCreateSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    # serializer_class = BorrowingListSerializer
    queryset = Borrowing.objects.select_related("user", "book")

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingListSerializer
