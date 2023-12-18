from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from registration.models import Attendee
from organizers.models import EmailRecipient, EmailSubject


class Command(BaseCommand):
    help = "Send lecture commencement notification emails to attendees"

    def handle(self, *args, **options):
        attendees = Attendee.objects.all()

        subject = "1445AH Whatsapp Group Chat Link!"
        total_mail_sent = 0
        for attendee in attendees:
            email_subject, created = EmailSubject.objects.get_or_create(subject=subject)
            email_recipient, recipient_created = EmailRecipient.objects.get_or_create(
                email=attendee.email
            )
            if not email_recipient.email_subjects.filter(id=email_subject.id).exists():
                html_message = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta http-equiv="X-UA-Compatible" content="IE=edge">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                </head>
                <body style="font-family: 'Arial', sans-serif;">

                    <div style="background-color: #f8f8f8; padding: 20px;">
                        <h2 style="color: #333333;">MSSNUI DAWRAH - 1445AH!</h2>
                    </div>

                    <div style="max-width: 600px; margin: 20px auto; padding: 20px; background-color: #ffffff;">
                        <p style="color: #333333;">
                            Dear {attendee.firsst_name},
                        </p>

                        <p style="color: #333333;">
                            Assalamu Alaikum!
                        </p>

                        <p style="color: #333333;">
                            We hope this message finds you in good health and high spirits. As part of our effort to enhance communication
                            and foster a sense of community among Dawrah participants, we have created a WhatsApp group.
                        </p>

                        <p style="color: #333333;">
                            Join the group to:
                        </p>

                        <ul style="color: #333333;">
                            <li>Receive important announcements.</li>
                            <li>Engage in discussions related to Dawrah topics.</li>
                            <li>Connect with fellow participants.</li>
                        </ul>

                        <p style="color: #333333;">
                            Click the link below to join:
                        </p>

                        <p style="text-align: center; margin-top: 20px;">
                            <a href="https://chat.whatsapp.com/KWBhJBobhj2HsUlXfvSpcu" style="background-color: #4CAF50; color: #ffffff; padding: 10px 15px; text-decoration: none; display: inline-block; border-radius: 5px;">
                                Join Dawrah WhatsApp Group
                            </a>
                        </p>

                        <p style="color: #333333;">
                            We look forward to your active participation and meaningful interactions in the group.
                        </p>

                        <p style="color: #333333;">
                            Best regards,<br>
                            The Dawrah Committee
                        </p>
                    </div>

                    <div style="background-color: #f1f1f1; padding: 10px; text-align: center;">
                        <p>&copy; 2023 The Dawrah Committee. All rights reserved.</p>
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
                    email.content_subtype = "html"
                    email.send(fail_silently=False)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Email sent to {attendee.first_name} {attendee.last_name} with email: {attendee.email}!"
                        )
                    )
                    email_recipient.email_subjects.add(email_subject)
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