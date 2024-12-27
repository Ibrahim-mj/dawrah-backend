from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.core.cache import cache
from django.db import transaction

from drf_spectacular.utils import extend_schema

from payments.utils import init_payment

from .serializers import AttendeeSerializer
from .models import Attendee


class RegistrationView(generics.CreateAPIView):
    """
    API endpoint that allows attendees to register for the event.

    Methods:
    POST -- Register a new attendee with the provided data.
    """

    serializer_class = AttendeeSerializer
    queryset = Attendee.objects.all()

    @extend_schema(tags=["Registration"])
    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        payment_url = init_payment(serializer.data["email"], 1000) # This pays 10 naira though.
        context = {
            "success": True,
            "message": "Registration successful. Please proceed to make your payment",
            "payment_url": payment_url,
            "data": serializer.data,
        }
        # I need to capture the serializers error and return them in a well formatted and consistent manner too
        return Response(context, status=status.HTTP_201_CREATED, headers=headers)
