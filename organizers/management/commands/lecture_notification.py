from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from registration.models import Attendee
from organizers.models import EmailRecipient

from django.conf import settings
import os


class Command(BaseCommand):
    help = "Send lecture commencement notification emails to attendees"

    def handle(self, *args, **options):
        attendees = Attendee.objects.all()

        subject = "Dawrah Weekend Kickoff!!!"
        total_mail_sent = 0
        for attendee in attendees:
            if not EmailRecipient.objects.filter(
                email=attendee.email, email_subject=subject
            ).exists():
                html_message = f"""
                <!DOCTYPE html>
                <html lang="en">

                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                </head>

                <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0;">

                    <div style="max-width: 600px; margin: 0 auto;">

                        <div style="padding: 20px;">

                        <p style="font-size: 16px;">
                        <strong>As-Salamu Alaikum Warahmatullahi Wabarakatuhu,</strong>
                        </p>

                        <p style="font-size: 16px;">
                            Dearest <strong>{attendee.first_name}</strong>,
                        </p>

                        <p style="font-size: 16px;">
                            It is with immense pleasure to officially announce to you that the Dawrah weekend has commenced. The place you
                            should be right now is the Central Mosque, University of Ibadan. Trust us, you won't want to miss a bit of the
                            invaluable guidance and insights unfolding there.
                        </p>

                        <p style="font-size: 16px;">
                            It is important to also note that all participants are expected to be with their form of identification to gain
                            access to all the essential kits for the event. May Allah subhaanuhu wata'aalaa make the knowledge beneficial to you.
                        </p>

                        <p style="font-size: 16px;">
                            Kindly find attached the itinerary and timetable of the event in the mail.
                        </p>

                        <p style="font-size: 16px;">
                            We're counting down to your presence, <strong>{attendee.first_name}</strong>!
                        </p>

                        <p style="font-size: 16px;">
                            Yours-in-Deen,
                            <br>
                            <strong>The Dawrah Committee</strong>
                        </p>

                        <div style="background-color: #f1f1f1; padding: 10px; text-align: center;">
                            <p>&copy; 2023 The Dawrah Committee. All rights reserved.</p>
                        </div>

                    </div>

                </body>

                </html>

                """
                try:
                    email = EmailMessage(
                        subject=subject,
                        body=html_message,
                        from_email="MSSNUI DAWRAH",
                        to=[attendee.email],
                    )
                    file_path = os.path.join(settings.BASE_DIR, "dawrah_timetable.docx")
                    email.attach_file(file_path)  # Add this line
                    email.content_subtype = (
                        "html"  # Add this line if you're sending an HTML email
                    )
                    email.send(fail_silently=False)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Email sent to {attendee.first_name} {attendee.last_name} with email: {attendee.email}!"
                        )
                    )
                    EmailRecipient.objects.create(
                        email_subject=subject,
                        email=attendee.email,
                    )
                    total_mail_sent += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(e))
                    self.stdout.write(
                        self.style.ERROR(
                            f"Email not sent to {attendee.first_name} {attendee.last_name} with email: {attendee.email}!"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(f"{total_mail_sent} mails sent successfully!")
        )
