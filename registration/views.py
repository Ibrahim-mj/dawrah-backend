from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.core.cache import cache
from django.db import transaction

from drf_spectacular.utils import extend_schema

from payments.utils import init_payment

from .serializers import AttendeeSerializer
from .models import Attendee


class RegistrationView(generics.CreateAPIView):
    serializer_class = AttendeeSerializer
    queryset = Attendee.objects.all()

    @extend_schema(tags=["Registration"])
    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        attendee = Attendee.objects.filter(email=email).first()

        if attendee:
            if attendee.dawrah_id:
                return Response({
                    "success": False,
                    "message": "You have already registered for this event.",
                    "paid": attendee.paid,
                    "data": {"email": attendee.email}
                }, status=status.HTTP_400_BAD_REQUEST)

            if not attendee.paid:
                payment_url = init_payment(attendee.email, 2030 * 100)
                return Response({
                    "success": False,
                    "message": "You have already registered but not paid yet. Please proceed to make your payment.",
                    "paid": attendee.paid,
                    "payment_url": payment_url,
                    "data": {
                        "email": attendee.email,
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        try:
            payment_url = init_payment(serializer.validated_data["email"], 2100 * 100)
        except Exception:
            return Response({
                "success": False,
                "message": "Failed to initialize payment. Please try again later."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "success": True,
            "message": "Registration successful. Please proceed to make your payment.",
            "payment_url": payment_url,
            "data": serializer.data,
        }, status=status.HTTP_201_CREATED, headers=headers)
