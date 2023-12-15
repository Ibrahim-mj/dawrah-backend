from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import filters

from registration.serializers import AttendeeSerializer
from registration.models import Attendee

from .serializers import UserCreateSerializer, UserSerializer
from .models import User

# from .permissions import CustomAdminPermission


class UserCreateView(generics.CreateAPIView):
    """
    View for creating a new user.

    Accepts POST requests with user data in the request body.
    Returns a JSON response with the newly created user data and a 201 status code on success.
    """

    serializer_class = UserCreateSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        context = {"message": "Account created successfully", "data": serializer.data}
        return Response(context, status=status.HTTP_201_CREATED, headers=headers)


class AllUsersListView(generics.ListAPIView):
    """
    A view that returns a paginated list of all users in the system.

    Only authenticated users with admin privileges are allowed to access this view.

    The list can be filtered by searching for specific fields, and sorted by
    id, email, first_name, last_name, is_staff, or is_active.

    Pagination is controlled by the 'page' and 'page_size' query parameters.
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    ordering_fields = [
        "id",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    ]
    search_fields = ["id", "email", "first_name", "last_name", "is_staff", "is_active"]


class UserDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    A view that allows authenticated admin users to retrieve, update, or delete a specific user.

    Methods:
    GET -- Retrieve a user instance.
    PUT -- Update a user instance.
    DELETE -- Delete a user instance.

    Required Arguments:
    pk -- The primary key of the user instance to retrieve, update, or delete.

    Returns:
    A JSON response containing the serialized user instance.
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]


class SingleAttendeeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AttendeeSerializer
    queryset = Attendee.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]


class AttendeeListView(generics.ListAPIView):
    """
    A view that returns a paginated list of all attendees in the system.

    Only authenticated users with admin privileges are allowed to access this view.

    The list can be filtered by searching for specific fields, and sorted by
    dawrah_id, first_name, last_name, email, or phone.

    Pagination is controlled by the 'page' and 'page_size' query parameters.

    serializer_class: The serializer class used to serialize the attendee objects.
    queryset: The queryset used to retrieve the attendee objects.
    permission_classes: The permission classes required to access this view.
    ordering_fields: The fields that can be used to sort the attendee objects.
    search_fields: The fields that can be used to search for specific attendee objects.
    """

    serializer_class = AttendeeSerializer
    queryset = Attendee.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    ordering_fields = [
        "dawrah_id",
        "first_name",
        "last_name",
        "email",
        "phone",
    ]
    search_fields = [
        "dawrah_id",
        "first_name",
        "last_name",
        "email",
        "phone",
    ]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        """
        Optionally restricts the returned response to a given user
        """
        queryset = Attendee.objects.all()
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        dawrah_id = self.request.query_params.get("dawrah_id")
        email = self.request.query_params.get("email")
        if first_name is not None:
            queryset = queryset.filter(first_name=first_name)
        if last_name is not None:
            queryset = queryset.filter(last_name=last_name)
        if dawrah_id is not None:
            queryset = queryset.filter(dawrah_id=dawrah_id)
        if email is not None:
            queryset = queryset.filter(email=email)
        else:
            queryset = queryset.all()
        return queryset
