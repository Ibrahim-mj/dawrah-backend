from django.urls import path

from . import views

urlpatterns = [
    path(
        "webhook/paystack/",
        views.PaystackWebhookView.as_view(),
        name="paystack-webhook",
    ),
    path(
        "event-payments-list/",
        views.EventPaymentListView.as_view(),
        name="event-payment-list",
    ),
    path(
        "event-payment/<int:pk>/",
        views.EventPaymentDetailView.as_view(),
        name="event-payment-detail",
    ),
    path("donation/", views.DonorCreateListView.as_view(), name="donation"),
    path("donation/<int:pk>/", views.DonorDetailView.as_view(), name="donation-detail"),
    path("payment-retry/", views.PaymentRetryView.as_view(), name="payment-retry"),
]
