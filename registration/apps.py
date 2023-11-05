from django.apps import AppConfig


class RegistrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "registration"

    """
    This module contains the registration app configuration.

    It includes the `ready` method which imports the `registration.signals` module.
    """

    def ready(self):
        import registration.signals
