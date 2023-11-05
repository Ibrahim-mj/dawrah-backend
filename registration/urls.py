from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegistrationView.as_view(), name="register"),
    path("donation/", views.DonorCreateListView.as_view(), name="donation"),
]
