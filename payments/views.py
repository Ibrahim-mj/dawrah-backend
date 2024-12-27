from django.db import transaction

from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import permissions

from drf_spectacular.utils import extend_schema

from payments.utils import init_payment, send_payment_retry_email
from registration.models import Attendee

from .models import Donor, EventPayment, Donation
from .serializers import DonorSerializer, EventPaymentSerializer, DonationSerializer
from registration.utils import generate_unique_id, send_confirmation_email


@extend_schema(tags=["Webhook"])
class PaystackWebhookView(APIView):
    @transaction.atomic
    @extend_schema(
        request=None,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "reference": {"type": "string"},
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                },
            },
            404: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                },
            },
            500: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                },
            },
        },
    )
    def post(self, request):
        signature = request.headers.get("x-paystack-signature")
        body = request.body

        # Ensure the payload is valid
        payload = request.data
        event = payload.get("event", "")
        data = payload.get("data", {})
        reference = data.get("reference", None)
        print(f"This is the value of the reference: {reference}")

        if not reference:
            return Response(
                {"success": False, "message": "Reference missing in payload"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if event == "charge.success":
                amount = data.get("amount", 0) / 100  # Convert amount to naira
                status_text = "success"

                # Attempt to update EventPayment or Donation
                try:
                    payment = EventPayment.objects.get(reference=reference)
                    payment.status = status_text
                    payment.amount = amount
                    payment.save()

                    attendee = payment.attendee
                    attendee.paid = True
                    generate_unique_id(attendee)
                    attendee.save()
                    send_confirmation_email(attendee)

                except EventPayment.DoesNotExist:
                    # Handle Donation
                    try:
                        donation = Donation.objects.get(reference=reference)
                        donation.status = status_text
                        donation.amount = amount
                        donation.save()
                    except Donation.DoesNotExist:
                        return Response(
                            {"success": False, "message": "Invalid reference"},
                            status=status.HTTP_404_NOT_FOUND,
                        )

                return Response(
                    {
                        "success": True,
                        "message": "Payment successful",
                        "reference": reference,
                    },
                    status=status.HTTP_200_OK,
                )

            elif event == "charge.failed":
                message = data.get("gateway_response", "Payment failed")
                status_text = "failed"

                # Update EventPayment or Donation
                try:
                    payment = EventPayment.objects.get(reference=reference)
                    payment.status = status_text
                    payment.save()
                    send_payment_retry_email(payment.attendee, reference, request)
                except EventPayment.DoesNotExist:
                    try:
                        donation = Donation.objects.get(reference=reference)
                        donation.status = status_text
                        donation.save()
                        send_payment_retry_email(donation.donor, reference, request)
                    except Donation.DoesNotExist:
                        return Response(
                            {"success": False, "message": "Invalid reference"},
                            status=status.HTTP_404_NOT_FOUND,
                        )

                return Response(
                    {"success": False, "message": message, "reference": reference},
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            print(str(e))
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(tags=["Payment"])
class EventPaymentListView(generics.ListAPIView):
    """
    EventPaymentListView is a view that handles the retrieval of event payments.
    Attributes:
        serializer_class (EventPaymentSerializer): The serializer class used to serialize the event payment data.
        queryset (QuerySet): The base queryset for retrieving event payments.
    Methods:
        get(request, *args, **kwargs):
            Handles GET requests to retrieve event payments.
            If a 'status' keyword argument is provided, filters the payments by the given status(success or failed).
            Otherwise, retrieves all event payments.
            Returns a JSON response with a message and the serialized payment data.
    """

    serializer_class = EventPaymentSerializer
    queryset = EventPayment.objects.all()

    @extend_schema(tags=["Payment"])
    def get(self, request, *args, **kwargs):
        payment_status = kwargs.get("status", None)
        if payment_status is not None:
            payments = self.queryset.filter(status=payment_status)
        else:
            payments = self.get_queryset()
        serializer = self.get_serializer(payments, many=True)
        context = {
            "message": "Payments retrieved successfully",
            "data": serializer.data,
        }
        return Response(context, status=status.HTTP_200_OK)


@extend_schema(tags=["Payment"])
class EventPaymentDetailView(generics.RetrieveAPIView):
    """
    EventPaymentDetailView is a view that handles the retrieval of a specific event payment.
    Attributes:
        serializer_class (EventPaymentSerializer): The serializer class used to serialize the event payment data.
        queryset (QuerySet): The base queryset for retrieving event payments.
    Methods:
        get(request, *args, **kwargs):
            Handles GET requests to retrieve a specific event payment.
            Returns a JSON response with a message and the serialized payment data.
    """

    serializer_class = EventPaymentSerializer
    queryset = EventPayment.objects.all()

    @extend_schema(tags=["Payment"])
    def get(self, request, *args, **kwargs):
        payment = self.get_object()
        serializer = self.get_serializer(payment)
        context = {
            "success": True,
            "message": "Payment retrieved successfully",
            "data": serializer.data,
        }
        return Response(context, status=status.HTTP_200_OK)


@extend_schema(tags=["Donation"])
class DonorCreateListView(generics.ListCreateAPIView):
    """
    API endpoint that allows donors to donate to the event.

    This view provides two methods:
    - GET: Retrieve a list of all donors.
    - POST: Register a new donor with the provided data.

    GET method is restricted to admin users only, while POST method is allowed to anyone.

    Attributes:
        serializer_class: The serializer class used to serialize and deserialize donor data.
        queryset: The queryset used to retrieve donors from the database.

    Methods:
        get_permissions: Returns the permission classes that apply to the current request.
        get: Handles GET requests and returns a list of all donors.
        post: Handles POST requests and registers a new donor with the provided data.
    """

    serializer_class = DonorSerializer
    queryset = Attendee.objects.all()

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [permissions.AllowAny]
        else:
            self.permission_classes = [permissions.IsAdminUser]
        return super(DonorCreateListView, self).get_permissions()

    @extend_schema(tags=["Donation"])
    def get(self, request, *args, **kwargs):
        donors = Donor.objects.all()
        serializer = self.get_serializer(donors, many=True)
        context = {"message": "Donors retrieved successfully", "data": serializer.data}
        return Response(context, status=status.HTTP_200_OK)

    @extend_schema(tags=["Donation"])
    def post(self, request, *args, **kwargs):
        serializer = DonorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        payment_url = init_payment(
            serializer.data["email"], serializer.data["amount"], donation=True
        )
        context = {
            "success": True,
            "message": "Donation successful. Thank you for your support",
            "payment_url": payment_url,
            "data": serializer.data,
        }
        return Response(context, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema(tags=["Donation"])
class DonorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that allows donors to donate to the event.

    This view provides three methods:
    - GET: Retrieve a specific donor.
    - PUT: Update a specific donor.
    - DELETE: Delete a specific donor.

    GET method is restricted to admin users only, while PUT and DELETE methods are allowed to anyone.

    Attributes:
        serializer_class: The serializer class used to serialize and deserialize donor data.
        queryset: The queryset used to retrieve donors from the database.

    Methods:
        get_permissions: Returns the permission classes that apply to the current request.
        get: Handles GET requests and returns a specific donor.
        put: Handles PUT requests and updates a specific donor.
        delete: Handles DELETE requests and deletes a specific donor.
    """

    serializer_class = DonorSerializer
    queryset = Donor.objects.all()

    def get_permissions(self):
        self.permission_classes = [permissions.IsAdminUser]
        return super(DonorDetailView, self).get_permissions()

    @extend_schema(tags=["Donation"])
    def get(self, request, *args, **kwargs):
        donor = self.get_object()
        serializer = self.get_serializer(donor)
        context = {"message": "Donor retrieved successfully", "data": serializer.data}
        return Response(context, status=status.HTTP_200_OK)

    @extend_schema(tags=["Donation"])
    def put(self, request, *args, **kwargs):
        donor = self.get_object()
        serializer = self.get_serializer(donor, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        context = {
            "success": True,
            "message": "Donor updated successfully",
            "data": serializer.data,
        }
        return Response(context, status=status.HTTP_200_OK)

    @extend_schema(tags=["Donation"])
    def delete(self, request, *args, **kwargs):
        donor = self.get_object()
        donor.delete()
        context = {"success": True, "message": "Donor deleted successfully"}
        return Response(context, status=status.HTTP_200_OK)


@extend_schema(tags=["Donation"])
class DonationListView(generics.ListAPIView):
    """
    DonorListView is a view that handles the retrieval of donors.
    Attributes:
        serializer_class (DonorSerializer): The serializer class used to serialize the donor data.
        queryset (QuerySet): The base queryset for retrieving donors.
    Methods:
        get(request, *args, **kwargs):
            Handles GET requests to retrieve donors.
            Returns a JSON response with a message and the serialized donor data.
    """

    serializer_class = DonationSerializer
    queryset = Donation.objects.all()

    @extend_schema(tags=["Donation"])
    def get(self, request, *args, **kwargs):
        donations = Donation.objects.all()
        serializer = self.get_serializer(donations, many=True)
        context = {
            "success": True,
            "message": "Donors retrieved successfully",
            "data": serializer.data,
        }
        return Response(context, status=status.HTTP_200_OK)


class PaymentRetryView(APIView):
    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "reference": {"type": "string"},
                },
                "required": ["reference"],
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "authorization_url": {"type": "string"},
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "message": {"type": "string"},
                },
            },
            404: {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "message": {"type": "string"},
                },
            },
            500: {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "message": {"type": "string"},
                },
            },
        },
        tags=["Payment"],
    )
    def post(self, request):
        reference = request.data.get("reference")
        if not reference:
            return Response(
                {"status": "error", "message": "Reference not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Look for the payment in both models
        payment = EventPayment.objects.filter(reference=reference).first()
        if not payment:
            payment = Donation.objects.filter(reference=reference).first()

        if not payment:
            return Response(
                {"status": "error", "message": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Extract email, amount, and callback URL
        email = payment.attendee.email
        amount = payment.amount
        callback_url = f"https://{settings.FE_URL}/payment-success"

        # Reinitialize payment using the utility function
        response_data = init_payment(email, amount, reference, callback_url)

        if response_data.get("status"):
            return Response(
                {
                    "status": "success",
                    "authorization_url": response_data["data"]["authorization_url"],
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"status": "error", "message": "Failed to initialize payment"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
