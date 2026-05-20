from django.urls import path

from .views import (
    CreateCheckoutSessionView, 
    CreatePaymentIntentView,
    stripe_webhook,
)


urlpatterns = [
    path(
        "create-checkout-session/",
        CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path(
        "create-payment-intent/",
        CreatePaymentIntentView.as_view(),
        name="create-payment-intent",
    ),
    path(
        "webhook/",
        stripe_webhook,
        name="stripe-webhook",
    ),
]