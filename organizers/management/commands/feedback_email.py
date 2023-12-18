from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from registration.models import Attendee
from organizers.models import EmailRecipient


class Command(BaseCommand):
    help = "Send lecture commencement notification emails to attendees"

    def handle(self, *args, **options):
        attendees = Attendee.objects.all()

        subject = "Your Feedback Matters!"
        total_mail_sent = 0
        for attendee in attendees:
            email_subject = EmailRecipient.objects.get_or_create(subject=subject)
            email_recipient, created = EmailRecipient.objects.get_or_create(
                email=attendee.email
            )
            if not email_recipient.email_subjects.filter(subject=subject).exists():
                html_message = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta http-equiv="X-UA-Compatible" content="IE=edge">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                </head>
                <body style="font-family: 'Arial', sans-serif;">

                    <p style="font-size: 16px; line-height: 1.6;">
                        <strong>As Salamu alaykum warahmotulahi wabarakatuhu</strong>
                    </p>

                    <p style="font-size: 16px; line-height: 1.6;">
                        <strong>Dear {attendee.first_name},</strong>
                    </p>

                    <p style="font-size: 16px; line-height: 1.6;">
                        We extend our heartfelt gratitude for your active participation in the Da'wah Weekend! Your presence has added immense value to the program, and we sincerely appreciate your commitment to seeking knowledge.
                    </p>

                    <p style="font-size: 16px; line-height: 1.6;">
                        How has your stay at the Da'wah Weekend been? How are the lectures so far? What have you learnt? Overall, how has the Dawrah been for you?
                    </p>

                    <p style="font-size: 16px; line-height: 1.6;">
                        Well, <strong>{attendee.first_name}</strong>, kindly take a moment to share your thoughts and experiences about the program. Your valuable input will help us plan future programs better.
                    </p>

                    <p style="font-size: 16px; line-height: 1.6;">
                        You can find the link to the form <a href="https://forms.gle/rzhs1dTU9CkCoRqPA" style="color: #3498db; text-decoration: none;"><strong>here</strong></a> to give us your feedback. This should not take up to 2 minutes of your time.
                    </p>

                    <p style="font-size: 16px; line-height: 1.6;">
                        May Allah (SWT) make this knowledge beneficial to you.
                    </p>

                    <p style="font-size: 16px; line-height: 1.6;">
                        JazakumuLlahu Khairan for your time and contribution.
                    </p>

                    <p style="font-size: 16px; line-height: 1.6;">
                        <strong>Yours-in-Islam,</strong><br>
                        <strong>The Dawrah Committee</strong>
                    </p>

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
