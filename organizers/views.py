from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from registration.serializers import AttendeeSerializer
from registration.models import Attendee

from .serializers import UserCreateSerializer, UserSerializer
from .models import User
from .permissions import CustomAdminPermission


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
    A view that returns a list of all users in the system.

    Only authenticated users with admin privileges are allowed to access this view.
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]


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


class AttendeeListView(generics.ListAPIView):
    """
    A view that returns a list of all attendees.

    Only authenticated users with admin privileges are allowed to access this view.
    """

    serializer_class = AttendeeSerializer
    queryset = Attendee.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]

class TokenObtainView(TokenObtainPairView):
    """
    View for authenticating a user and generating an access token and a refresh token.

    Accepts POST requests with user credentials in the request body.
    Returns a JSON response with the access token and the refresh token on success.

    Inherits from TokenObtainPairView, which is a built-in view that handles token-based authentication.
    Uses the IsAdminUser permission class to restrict access to admin users only.
    """
    permission_classes = [CustomAdminPermission]

class TokenRefreshView(TokenRefreshView):
    """
    View for refreshing an access token.

    Accepts POST requests with a refresh token in the request body.
    Returns a JSON response with a new access token on success.

    Inherits from TokenRefreshView, which is a built-in view that handles token-based authentication.
    Uses the IsAdminUser permission class to restrict access to admin users only.
    """
    permission_classes = [CustomAdminPermission]
