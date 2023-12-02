from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.core.cache import cache

from .serializers import AttendeeSerializer, DonorSerializer, ExistingEmailSerializer
from .models import Attendee, Donor


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
        if self.request.method == "POST":
            self.permission_classes = [permissions.AllowAny]
        else:
            self.permission_classes = [permissions.IsAdminUser]
        return super(DonorCreateListView, self).get_permissions()

    def get(self, request, *args, **kwargs):
        donors = Donor.objects.all()
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

    def get(self, request, *args, **kwargs):
        donor = self.get_object()
        serializer = self.get_serializer(donor)
        context = {"message": "Donor retrieved successfully", "data": serializer.data}
        return Response(context, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        donor = self.get_object()
        serializer = self.get_serializer(donor, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        context = {
            "message": "Donor updated successfully",
            "data": serializer.data,
        }
        return Response(context, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        donor = self.get_object()
        donor.delete()
        context = {"message": "Donor deleted successfully"}
        return Response(context, status=status.HTTP_200_OK)


class ExistingEmailView(generics.ListAPIView):
    """
    API endpoint that returns a list of existing email addresses of attendees.
    """

    serializer_class = ExistingEmailSerializer
    queryset = Attendee.objects.all()

    def get_cached_data(self):
        """
        Helper method to retrieve data from cache.
        """
        cache_key = "existing_emails_cache_key"

        # Try to get data from cache
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        # If data is not in cache, fetch and cache it
        existing_emails = list(Attendee.objects.values_list("email", flat=True))
        cache.set(cache_key, existing_emails, timeout=60)  # Cache for 1 minute
        return existing_emails

    def get(self, request, *args, **kwargs):
        # Retrieve data from cache or fetch and cache if not present
        existing_emails = self.get_cached_data()

        return Response(existing_emails, status=status.HTTP_200_OK)
