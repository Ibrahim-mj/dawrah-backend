from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from registration.models import Attendee


class Command(BaseCommand):
    help = "Send program commencement notification emails to attendees"

    def handle(self, *args, **options):
        attendees = Attendee.objects.all()

        for attendee in attendees:
            if attendee.email == "theclassasake@gmail.com":
                continue
            message = f"""
            As-Salamu Alaikum Warahmatullahi Wabarakatuh,

            Dear {attendee.first_name} {attendee.last_name},

            We hope this message finds you well and eagerly anticipating the upcoming Dawrah event starting tomorrow, the 15th of December. To ensure a smooth and hassle-free experience for all participants, we would like to provide you with essential details regarding the collection of the Dawrah booklet and Meal tickets.

            Location for Ticket Collection: Central Masjid.

            Time: Immediately After Jumuah until Asr.

            The program starts immediately after Asr.

            Please ensure you bring the following for ticket collection:

            A valid form of identification confirming your status as a UI student (ID card, library ID, Hall ID, etc.).

            Your Dawrah ID. Be reminded that your ID is: {attendee.dawrah_id}

            Please note that tickets will only be distributed during the specified time frame mentioned above. Kindly ensure your punctuality to avoid inconvenience.

            Best regards,
            The Dawrah Committee.
            """
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

                        <p>As-Salamu Alaikum Warahmatullahi Wabarakatuh,</p>

                        <p>Dear <strong>{attendee.first_name} {attendee.last_name}</strong>,</p>

                        <p>We hope this message finds you well and eagerly anticipating the upcoming Dawrah event starting today,
                            the 15th of December. To ensure a smooth and hassle-free experience for all participants, we would like
                            to provide you with essential details regarding the collection of the Dawrah booklet and Meal tickets.
                        </p>

                        <p><strong>Location for Ticket Collection:</strong> Central Masjid.</p>

                        <p><strong>Time:</strong> Immediately After Jumuah until Asr.</p>

                        <p>The program starts <strong>immediately after Asr</strong>.</p>

                        <p>Please ensure you bring the following for ticket collection:</p>

                        <ol>
                            <li>A valid form of identification confirming your status as a UI student (ID card, library ID, Hall ID,
                                etc.).
                            </li>
                            <li>Your Dawrah ID. Be reminded that your ID is: <strong>{attendee.dawrah_id}</strong></li>
                        </ol>

                        <p>Please note that tickets will only be distributed during the specified time frame mentioned above. Kindly
                            ensure your punctuality to avoid inconvenience.</p>

                        <p>Best regards,</p>
                        <p><strong>The Dawrah Committee.</strong></p>
                    </div>

                    <div style="background-color: #f1f1f1; padding: 10px; text-align: center;">
                        <p>&copy; 2023 The Dawrah Committee. All rights reserved.</p>
                    </div>

                </div>

            </body>

            </html>

            """
            send_mail(
                subject="The Long Awaited Dawrah is here!!",
                message=message,
                from_email="MSSNUI DAWRAH",
                recipient_list=[attendee.email],
                fail_silently=False,
                html_message=html_message,
            )

        self.stdout.write(self.style.SUCCESS("Emails sent successfully!"))
