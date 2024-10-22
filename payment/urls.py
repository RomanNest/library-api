from django.urls import path, include
from rest_framework import routers

from payment.views import (
    PaymentViewSet,
    PaymentSuccessView,
    PaymentCancelView,
)


router = routers.DefaultRouter()
router.register("payment", PaymentViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
    path("success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
]

app_name = "payment"
