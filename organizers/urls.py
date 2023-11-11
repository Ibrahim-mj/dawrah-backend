from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.UserCreateView.as_view(), name="register"),
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
]
