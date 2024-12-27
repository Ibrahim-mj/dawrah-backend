from django.db import models

from registration.models import Attendee


class Donor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=100)
    amount = models.PositiveIntegerField()
    donated = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class EventPayment(models.Model):
    attendee = models.ForeignKey(
        Attendee, on_delete=models.CASCADE, related_name="payments"
    )
    reference = models.CharField(
        max_length=100, unique=True
    )  # Paystack transaction reference
    status = models.CharField(max_length=50)  # success/failed
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.CharField(max_length=255, null=True, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.attendee.first_name} {self.attendee.last_name} - {self.status}"


class Donation(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name="payments")
    reference = models.CharField(
        max_length=100, unique=True
    )  # Paystack transaction reference
    status = models.CharField(max_length=50)  # success/failed
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.CharField(max_length=255, null=True, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)
