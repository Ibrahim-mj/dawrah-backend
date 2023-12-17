from django.core.management import call_command


def send_notification_email():
    call_command("notification_email")
