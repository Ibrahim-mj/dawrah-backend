import random
import string
import time

import requests

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from .models import EventPayment, Donation
from registration.models import Attendee


def init_payment(email, amount, donation=False, existing_reference=None):
    """
    Initialize a Paystack payment for the given email and amount.

    Args:
        email (str): Email of the attendee initiating the payment.
        amount (int): Payment amount in kobo (smallest currency unit).

    Returns:
        str: The Paystack authorization URL for completing the payment if successful.
        None: If the payment initialization fails.

    Notes:
        - Ensures the payment is recorded in the database with 'initialized' status.
        - Expects the email to match an attendee in the database.
        - Verifies the Paystack response and handles errors gracefully.
    """

    paystack_url = "https://api.paystack.co/transaction/initialize"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

    random_string = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=6)
    )  # for generating unique reference
    reference = existing_reference or f"REG-{int(time.time())}-{random_string}"
    data = {
        "email": email,
        "amount": amount,
        "reference": reference,
        "callback_url": f"https://{settings.FE_URL}/payment-success",
    }
    response = requests.post(paystack_url, headers=headers, json=data)
    response_data = response.json()

    if response_data["status"]:
        attendee = Attendee.objects.filter(email=email).first()
        if not attendee:
            raise ValueError("Attendee not found for the provided email.")
        if donation:
            payment, created = Donation.objects.get_or_create(
                reference=reference,
                defaults={
                    "attendee": attendee,
                    "amount": amount,
                    "status": "initialized",
                },
            )
        else:
            payment, created = EventPayment.objects.get_or_create(
                reference=reference,
                defaults={
                    "attendee": attendee,
                    "amount": amount,
                    "status": "initialized",
                },
            )

        if not created:
            payment.status = "initialized"
            payment.save()

        return response_data["data"]["authorization_url"]
    return None


def send_payment_retry_email(attendee, reference, request):
    # retry_url = request.build_absolute_uri(reverse("payments:payment-retry", kwargs={"reference": reference}))
    retry_url = f"{settings.FE_URL}/retry-payment?reference={reference}"
    send_mail(
        subject="Dawrah - Payment Retry Link",
        message=f"You can retry your payment by clicking the link below:\n{retry_url}",
        from_email="MSSNUI DAWRAH",
        recipient_list=[attendee.email],
        fail_silently=False,
    )
