from urllib.parse import urlencode

from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.db import transaction

import jwt
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import filters
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from registration.serializers import AttendeeSerializer
from registration.models import Attendee

from .serializers import PasswordResetSerializer, ResendVerificationEmailSerializer, SetNewPasswordSerializer, UserCreateSerializer, UserSerializer
from .models import User, UserProviderEnum
from .utils import oauth

from .utils import oauth, decode_token, send_verification, send_reset_password


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
        send_verification(user, request)
        context = {
            "success": True,
            "message": "Your account has been created. Kindly check your email for verification link.",
        }
        return Response(context, status=status.HTTP_201_CREATED, headers=headers)
    

class AccountVerificationView(generics.RetrieveAPIView):
    """
    AccountVerificationView handles the verification of user accounts through a token-based mechanism.

    This view extends Django Rest Framework's RetrieveAPIView to provide a read-only endpoint.
    It is designed to decode a verification token sent to the user, verify its validity, and update the user's account status accordingly.

    Attributes:
        queryset: Specifies the queryset that this view will operate on. Here, it is set to all User objects.
        serializer_class: Points to the serializer class that should be used for serializing and deserializing data.

    Methods:
        get_object(self):
            Attempts to decode the provided token to find the corresponding user.
            - Returns: The User object if the token is valid and the user exists.
            - Raises: Http404 with an appropriate error message if the token is expired, invalid, or the user does not exist.

        retrieve(self, request, *args, **kwargs):
            Overrides the default retrieve method to verify the user's account upon successful verification.
            - Parameters:
                - request: The HttpRequest object.
                - *args: Variable length argument list.
                - **kwargs: Arbitrary keyword arguments.
            - Returns: HttpResponseRedirect to a URL with the verification status. The URL includes query parameters indicating the success or failure of the verification process, along with relevant user data and tokens if successful.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        """
        Decodes the token and gets the user object

        Returns:
            User: The User object if the token is valid and the user exists.

        Raises:
            Http404: If the token is expired, invalid, or the user does not exist.
        """

        token = self.kwargs.get("token")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["id"])
            return user
        except jwt.ExpiredSignatureError:
            raise Http404("Verification link has expired. Please request a new one.")
        except jwt.InvalidTokenError:
            raise Http404("Invalid token. Please request a new one.")
        except User.DoesNotExist:
            raise Http404("User does not exist.")

    def retrieve(self, request, *args, **kwargs):
        """
        Activates the user account

        Parameters:
            request (HttpRequest): The HttpRequest object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponseRedirect: Redirects to a URL with the verification status. The URL includes query parameters indicating the success or failure of the verification process, along with relevant user data and tokens if successful.
        """

        redirect_url = settings.VERIFY_EMAIL_REDIRECT_URL
        # And I can actually use urlparse(redirect_url).netloc to if it is absolute;
        # If not, user request.build_absolute_url
        try:
            user = self.get_object()
            user.is_verified = True
            user.save()
            user_data = self.serializer_class(user).data
            url = f'{redirect_url}?{urlencode({"success": True, "message": "user verified successfully", "data": user_data, "tokens": user.get_tokens_for_user()})}'
            return HttpResponseRedirect(url)
        except Exception as e:
            url = f"{redirect_url}?{urlencode({'success': False, 'message': 'An error occurred while verifying the user.', 'error': str(e) })}"
            return HttpResponseRedirect(url)


class ResendVerificationEmailView(generics.GenericAPIView):
    """
    Takes email address, redirect_url and resend verification email to user.

    This view is responsible for handling the resend verification email functionality.
    It takes the email address and redirect URL from the request data and attempts to resend the verification email to the user.
    If the user is already verified, it returns a response indicating that the user is already verified.
    If the user does not exist, it returns a response indicating that a user with that email does not exist.
    If an error occurs while sending the verification email, it returns a response with an error message.

    Methods:
    - post: Handles the POST request and performs the resend verification email logic.
    """

    serializer_class = ResendVerificationEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            if user.is_verified:
                return Response(
                    {
                        "success": False,
                        "message": "User is already verified.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            send_verification(user, request)
            return Response(
                {"success": True, "message": "Verification email has been sent."},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "User with that email does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"An error occurred while sending the verification email. {e}. Please try again later.",  # May ot be wise to include the exception here
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RequestPasswordResetView(generics.GenericAPIView):
    """
    Sends a password reset link to the provided email if user with that email exists.

    Methods:
    - post: Sends a password reset link to the provided email if user with that email exists.
    """

    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        """
        Sends a password reset link to the provided email if user with that email exists.

        Parameters:
        - request: The HTTP request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - If the password reset link is sent successfully, returns a success response with a message.
        - If the user does not exist or is not active, returns an error response with a message.
        """
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            if user.auth_provider != User.AUTH_PROVIDERS["email"]:
                message = {
                    "success": False,
                    "message": "You did not sign up with email and password",
                }
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            elif user.is_verified:
                send_reset_password(user)
                message = {
                    "success": True,
                    "message": "A password reset link has been sent to your mail.",
                }
                return Response(message, status=status.HTTP_200_OK)

        else:
            message = {
                "success": False,
                "message": "No active user with that email exists.",
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(generics.GenericAPIView):
    """
    Takes the token and a new password and resets the user's password

    Methods:
    - patch: Resets the user's password using the provided token and new password.
    """

    serializer_class = SetNewPasswordSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = request.data.get("token")
        password = serializer.validated_data["password"]
        try:
            payload = decode_token(token)
            user = User.objects.get(pk=payload["id"])
            user.set_password(password)
            user.save()
            response = {"success": True, "message": "Password reset successful."}
            return Response(response, status=status.HTTP_200_OK)
        except ValueError as e:
            response = {"success": False, "message": str(e)}
            return Response()


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


# =================================================


class PairTokenObtainView(TokenObtainPairView):
    """
    View to obtain both access and refresh tokens for a user.
    """

    @extend_schema(
        description="View to obtain both access and refresh tokens for a user.",
        responses={
            200: {
                "description": "Token obtained successfully.",
                "content": {
                    "application/json": {
                        "example": {
                            "success": True,
                            "message": "Token obtained successfully.",
                            "tokens": {
                                "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNzg2Njk0MCwiaWF0IjoxNzM1Mjc0OTQwLCJqdGkiOiJkNWQyYmU4MmIzMmQ0ZmM4YWUxYWRmN2RiY2RlODhkZCIsInVzZXJfaWQiOjF9.46-n-XJZoDm2j_PZfH2RtDSZy3NrmS-J_Iho0eRIvc8",
                                "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM2NTcwOTQwLCJpYXQiOjE3MzUyNzQ5NDAsImp0aSI6Ijg3ZjQ4N2YwNDY4ZDQzZDA4ZmQzOTA1MzRlYWQ1Mjg4IiwidXNlcl9pZCI6MX0.D68SLFC6U5GGpwINI-0mJlD3xoE0R1ukZIPskSHd9do",
                                "email": "user@example.com",
                                "first_name": "First Name",
                                "last_name": "Last Name",
                                "is_staff": False,
                            },
                        }
                    }
                },
            }
        },
        tags=["auth"],
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = User.objects.get(email=request.data["email"])
        tokens = {
            "success": True,
            "message": "Token obtained successfully.",
            "tokens": response.data,
        }
        return Response(tokens, status=status.HTTP_200_OK)


class RefreshTokenView(TokenRefreshView):
    """
    A view for refreshing authentication tokens.

    This view extends the `TokenRefreshView` class provided by the Django Rest Framework SimpleJWT library.
    It handles the POST request to refresh an existing authentication token and returns a new token.

    Methods:
    - post: Handles the POST request to refresh the token and returns the new token.

    """

    @extend_schema(
        description="A view for refreshing authentication tokens.",
        responses={200: "Token obtained successfully."},
        tags=["auth"],
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        tokens = {
            "success": True,
            "message": "Token obtained successfully.",
            "tokens": response.data,
        }
        return Response(tokens, status=status.HTTP_200_OK)


@extend_schema(tags=["auth"])
class GoogleSignInView(APIView):
    """
    View for handling Google sign-in.

    This view redirects the user to the Google sign-in page for authentication.

    Methods:
        - get: Handles the GET request and redirects the user to the Google sign-in page.
    """

    def get(self, request):
        google = oauth.create_client("google")
        redirect_url = request.build_absolute_uri(
            reverse("organizers:google-signin-callback")
        )
        return google.authorize_redirect(request, redirect_url)


@extend_schema(tags=["auth"])
class GoogleSignInCallbackView(APIView):
    """
    View for handling the Google sign-in callback.

    This view is responsible for handling the callback from Google after a user has successfully signed in.
    It retrieves the user's profile information from Google and performs the necessary actions based on whether
    the user already exists or needs to be created.

    If the user already exists, the view generates a new access token and refresh token for the user.
    Else, it creates a new user account and redirects the user to the appropriate URL.

    Methods:
        - get: Handles the GET request for the Google sign-in callback.

    """

    @transaction.atomic()
    def get(self, request):
        """
        Handles the GET request for the Google sign-in callback.

        This method retrieves the access token from the request, fetches the user's profile information from Google,
        and performs the necessary actions based on whether the user already exists or needs to be created.

        Returns:
            A response indicating the success or failure of the login or registration process.

        """
        token = oauth.google.authorize_access_token(request)
        resp = oauth.google.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", token=token
        )
        resp.raise_for_status()
        profile = resp.json()

        user = User.objects.filter(email=profile["email"]).first()
        if user is not None:
            if user.auth_provider != User.AUTH_PROVIDERS["google"]:
                redirect_url = f"{settings.GOOGLE_SIGNIN_REDIRECT_URL}?{urlencode({{'success': False, 'message': 'You did not sign up with Google'}})}"
                return HttpResponseRedirect(redirect_url)
            # maybe restrict unapproved students here too.
            tokens = user.get_tokens_for_user()
            redirect_url = f"{settings.GOOGLE_SIGNIN_REDIRECT_URL}?{urlencode({'success': True, 'message': 'Login successful.', 'tokens': tokens})}"
            return HttpResponseRedirect(redirect_url)
        else:
            password = get_random_string(10)
            # How do I get the user's phone number from google bai?? E still dey fail
            user = User.objects.create_user(
                profile["email"],
                password=password,
                auth_provider=UserProviderEnum.GOOGLE,
                first_name=profile["given_name"],
                last_name=profile["family_name"],
                is_verified=True,
            )
            user.save()
            redirect_url = f"{settings.GOOGLE_SIGNIN_REDIRECT_URL}?{urlencode({'success': True, 'message': 'Registration Successful', 'data': {'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name}, 'tokens': user.get_tokens_for_user()})}"
            return HttpResponseRedirect(redirect_url)