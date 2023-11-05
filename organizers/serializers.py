from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core import validators

from .models import User


class UserCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        max_length=100,
        validators=[
            validators.RegexValidator(r"^[a-zA-Z ]+$", "Name must be letters only"),
        ],
        error_messages={
            "required": "Please enter your first name",
            "blank": "Please enter your first name",
        },
    )

    last_name = serializers.CharField(
        max_length=100,
        validators=[
            validators.RegexValidator(r"^[a-zA-Z ]+$", "Name must be letters only"),
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
                queryset=User.objects.all(), message="Email already exists"
            ),
        ],
        error_messages={
            "required": "Please enter your email",
            "blank": "Please enter your email",
        },
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects._create_user(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ("id",)
