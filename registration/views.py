from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .serializers import AttendeeSerializer, DonorSerializer, ExistingEmailSerializer
from .models import Attendee


class RegistrationView(generics.CreateAPIView):
    """
    API endpoint that allows attendees to register for the event.

    Methods:
    POST -- Register a new attendee with the provided data.
    """

    serializer_class = AttendeeSerializer
    queryset = Attendee.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        context = {
            "message": "Registration successful. Please check your email for your dawrah ID",
            "data": serializer.data,
        }
        return Response(context, status=status.HTTP_201_CREATED, headers=headers)


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
        if self.request.method == "GET":
            self.permission_classes = [permissions.IsAdminUser]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super(DonorCreateListView, self).get_permissions()

    def get(self, request, *args, **kwargs):
        donors = Attendee.objects.filter(donor=True)
        serializer = self.get_serializer(donors, many=True)
        context = {"message": "Donors retrieved successfully", "data": serializer.data}
        return Response(context, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = DonorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        context = {
            "message": "Donation successful. Thank you for your support",
            "data": serializer.data,
        }
        return Response(context, status=status.HTTP_201_CREATED, headers=headers)

class ExistingEmailView(generics.ListAPIView):
    """
    API endpoint that returns a list of existing email addresses of attendees.
    """
    serializer_class = ExistingEmailSerializer

    def get(self, request, *args, **kwargs):
        existing_emails = Attendee.objects.values_list("email", flat=True)
        return Response(existing_emails, status=status.HTTP_200_OK)