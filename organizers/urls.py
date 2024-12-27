from django.urls import path

from . import views

app_name = "organizers"

urlpatterns = [
    path("register/", views.UserCreateView.as_view(), name="register"),
    path(
        "verify/<str:token>/",
        views.AccountVerificationView.as_view(),
        name="verify-email",
    ),
    path(
        "resend-verification-email/",
        views.ResendVerificationEmailView.as_view(),
        name="resend-verification-email",
    ),
    path(
        "request-password-reset/",
        views.RequestPasswordResetView.as_view(),
        name="request-password-reset",
    ),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
    path("attendee-list/", views.AttendeeListView.as_view(), name="attendee-list"),
    path(
        "attendee-list/<str:pk>/",
        views.SingleAttendeeView.as_view(),
        name="attendee-detail",
    ),
    path("users/", views.AllUsersListView.as_view(), name="user"),
    path(
        "users/<int:pk>/",
        views.UserDetailUpdateDeleteView.as_view(),
        name="user-detail",
    ),
    path(
        "obtain-token/",
        views.PairTokenObtainView.as_view(),
        name="obtain-token",
    ),
    path(
        "refresh-token/",
        views.RefreshTokenView.as_view(),
        name="refresh-token",
    ),
    path(
        "google-signin/",
        views.GoogleSignInView.as_view(),
        name="google-signin",
    ),
    path(
        "google-signin-callback/",
        views.GoogleSignInCallbackView.as_view(),
        name="google-signin-callback",
    ),
]
