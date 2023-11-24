from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core import validators

from .models import Attendee, Donor


class AttendeeSerializer(serializers.ModelSerializer):
    """
    Serializer for Attendee model. Serializes and deserializes Attendee objects to and from JSON format.
    """

    dawrah_id = serializers.CharField(
        read_only=True,
    )
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
            UniqueValidator(
                queryset=Attendee.objects.all(), message="Email already exists"
            ),
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

    level_of_study = serializers.IntegerField(
        error_messages={
            "required": "Please enter your level of study",
            "blank": "Please enter your level of study",
        },
        validators=[
            validators.MinValueValidator(100, message="Level can not be less than 100"),
            validators.MaxValueValidator(
                700, message="Level can not be greater than 700"
            ),
            validators.RegexValidator(
                r"^(100|200|300|400|500|600|700)$",
                "Level must be a hundred between 100 and 700",
            ),
        ],
    )

    department = serializers.CharField(
        validators=[
            validators.RegexValidator(
                r"^[a-zA-Z-' ,.()&]+$",
                "Department name can include letters, hyphens, apostrophes, commas, periods, parentheses, and ampersands",
            ),
        ],
        error_messages={
            "required": "Please enter your department",
            "blank": "Please enter your department",
        },
    )

    level = serializers.ChoiceField(
        choices=Attendee.LEVEL_CHOICES,
        error_messages={
            "required": "Please select your level",
            "blank": "Please select your level",
        },
    )

    class Meta:
        model = Attendee
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "department",
            "level_of_study",
            "level",
            "dawrah_id",
        )


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


class ExistingEmailSerializer(serializers.ModelSerializer):
    """
    Serializer for checking already email addresses in the data.
    """

    class Meta:
        model = Attendee
        fields = ("email",)
