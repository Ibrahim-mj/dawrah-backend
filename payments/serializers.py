from rest_framework import serializers

from django.core import validators

from .models import Donor

from .models import EventPayment, Donation


class EventPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPayment
        fields = "__all__"


class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = "__all__"


class DonorSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        max_length=100,
        validators=[
            validators.RegexValidator(
                r"^[a-zA-Z-' ]+$",
                "Name must include letters, hyphens, or apostrophes only",
            ),
        ],
        error_messages={
            "required": "Please enter your first name",
            "blank": "Please enter your first name",
        },
    )

    last_name = serializers.CharField(
        max_length=100,
        validators=[
            validators.RegexValidator(
                r"^[a-zA-Z-' ]+$",
                "Name must include letters, hyphens, or apostrophes only",
            ),
        ],
        error_messages={
            "required": "Please enter your last name",
            "blank": "Please enter your first name",
        },
    )

    email = serializers.EmailField(
        validators=[
            validators.EmailValidator(),
        ],
    )

    phone = serializers.CharField(
        validators=[
            validators.RegexValidator(
                r"^(?:\+234|0)[789]\d{9}$", "Enter a valid Nigerian phone number"
            )
        ],
        error_messages={
            "required": "Please enter your phone number",
            "blank": "Please enter your phone number",
        },
    )

    amount = serializers.IntegerField(
        error_messages={
            "required": "Please enter your amount",
            "blank": "Please enter your amount",
        },
    )

    class Meta:
        model = Donor
        fields = "__all__"
