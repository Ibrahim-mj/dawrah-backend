import threading

from django.db.models.signals import pre_save, post_save
from django.core.mail import send_mail
from django.conf import settings

from datetime import datetime

from .models import Attendee

class EmailThread(threading.Thread):
    def __init__(self, subject: str, message: str, html_message: str, recipients: list):
        self.subject = subject
        self.message = message
        self.html_message = html_message
        self.recipients = recipients
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            subject=self.subject,
            message=self.message,
            from_email=f"MSSNUI DAWRAH",
            html_message=self.html_message,
            recipient_list=self.recipients,
            fail_silently=False,
        )


def get_last_id():
    """
    Returns the Dawrah ID of the last attendee in the database, or None if there are no attendees.
    """
    last_attendee = Attendee.objects.all().last()
    return last_attendee.dawrah_id if last_attendee else None


def send_confirmation_email(instance, **kwargs):
    """
    Sends a confirmation email to the attendee after they have registered.
    """
    if instance.dawrah_id is not None:
        subject="Dawrah Registration Confirmation"
        recipients = [instance.email]    
        message = f"Assalamu alaikum wa rahmatullahi wa barakatuhu, {instance.first_name} {instance.last_name}. Thank you for registering for the Dawrah. Your Dawrah ID is {instance.dawrah_id}. Kindly keep this ID safe as you will need it to access the Dawrah. Kindly join the WhatsApp group for dawrah here: https://chat.whatsapp.com/DrePaR6GU6BIUZTMz1poHn?mode=ac_t We look forward to seeing you at the Dawrah, inshaAllah."
        html_message = f"""
        <html>
            <body>
                <p>Assalamu 'alaykum wa rahmatullahi wa barakatuhu, <strong>{instance.first_name} {instance.last_name}</strong>.</p>
                <p>Thank you for registering for the Dawrah program.</p>
                <p>Your Dawrah ID is <strong>{instance.dawrah_id}</strong>.</p>
                <p>Kindly keep this ID safe as you will need it to access the program.</p>
                <p>Kindly join the WhatsApp group for the Dawrah here: <a href="https://chat.whatsapp.com/DrePaR6GU6BIUZTMz1poHn?mode=ac_t">Join WhatsApp Group</a></p>
                <p>We look forward to seeing you at the Dawrah, inshaAllah.</p>
            </body>
        </html>
        """
        EmailThread(subject, message, html_message, recipients).start()
        
        # send_mail(
        #     subject="Dawrah Registration Confirmation",
        #     message=message,
        #     from_email="MSSNUI DAWRAH",
        #     recipient_list=[instance.email],
        #     fail_silently=False,
        #     html_message=html_message,
        # )

def generate_unique_id(instance, **kwargs):
    """
    Generates a unique ID for a Dawrah instance if it doesn't already have one.
    The ID is in the format 'DWR-YYNN', where YY is the last two digits of the current year
    and NN is a four-digit number starting from 0001 and incrementing by 1 for each new ID.
    """
    if not instance.dawrah_id:
        last_id = get_last_id()
        current_year = datetime.now().year % 100
        if last_id is not None and isinstance(last_id, str) and "-" in last_id:
            new_id = int(last_id.split("-")[1]) + 1
            new_id = "SDW-" + str(new_id).zfill(4)
        else:
            new_id = "SDW-" + str(current_year).zfill(2) + "01"
        instance.dawrah_id = new_id