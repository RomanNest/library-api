from django.urls import path, include
from rest_framework import routers

from payment.views import (
    PaymentViewSet,
    PaymentSuccessView,
    PaymentCancelView,
    PaymentRenewView,
)


router = routers.DefaultRouter()
router.register("payment", PaymentViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
    path("success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
    path("renew/", PaymentRenewView.as_view(), name="payment-renew"),
]

app_name = "payment"
