import jwt

from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from core.utils import EmailThread

oauth = OAuth()

google_config = settings.AUTHLIB_OAUTH_CLIENTS["google"]
oauth.register(
    name="google",
    client_id=google_config["client_id"],
    client_secret=google_config["client_secret"],
    authorize_url=google_config["authorize_url"],
    authorize_params=google_config["authorize_params"],
    access_token_url=google_config["access_token_url"],
    access_token_params=google_config["access_token_params"],
    client_kwargs=google_config["client_kwargs"],
    jwks_uri=google_config["jwks_uri"],
)


def decode_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
    return payload


def send_verification_email(verification_link, user) -> None:
    subject = "Event App - Verify your email"
    message = f"Hello {user.first_name},\n\nPlease verify your email by clicking on the link below:\n\n{verification_link}\n\nThis link will expire in 24 hours.\n\nIf you did not register for an account, please ignore this email.\n\nBest regards,\nEvent App Team"
    html_message = f"<p>Hello {user.first_name},</p><p>Please verify your email by clicking on the link below:</p><p><a href='{verification_link}'>Verify Email</a></p><p>This link will expire in 24 hours.</p><p>If you did not register for an account, please ignore this email.</p><p>Best regards,<br>Event App Team</p>"
    recipients = [user.email]
    EmailThread(subject, message, html_message, recipients).start()


def send_verification(user, request) -> None:  # TODO: add error logging
    token = user.generate_jwt_token()
    verification_link = request.build_absolute_uri(
        reverse("users:verify-email", kwargs={"token": token})
    )
    send_verification_email(verification_link, user)


def send_reset_password_email(password_reset_link, user) -> None:
    subject = "Event App - Reset your password"
    message = f"Hello {user.first_name},\n\nYou requested a password reset. Please reset your password by clicking on the link below:\n\n{password_reset_link}\n\nThis link will expire in 24 hours.\n\nIf you did not request a password reset, please ignore this email.\n\nBest regards,\nEvent App Team"
    html_message = f"<p>Hello {user.first_name},</p><p>You requested a password reset. Please reset your password by clicking on the link below:</p><p><a href='{password_reset_link}'>Reset Password</a></p><p>This link will expire in 24 hours.</p><p>If you did not request a password reset, please ignore this email.</p><p>Best regards,<br>Event App Team</p>"
    recipients = [user.email]
    EmailThread(subject, message, html_message, recipients).start()


def send_reset_password(user) -> None:
    token = user.generate_jwt_token()
    password_reset_link = f"{settings.RESET_PASSWORD_REDIRECT_URL}?token={token}"
    send_reset_password_email(password_reset_link, user)