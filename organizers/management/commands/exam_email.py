from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from registration.models import Attendee
from organizers.models import EmailRecipient, EmailSubject


class Command(BaseCommand):
    help = "Send lecture commencement notification emails to attendees"

    def handle(self, *args, **options):
        attendees = Attendee.objects.all()

        subject = "Exam - Time to Test Your Knowledge!"
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

                    <p>As-Salamu Alaikum Warahmatullahi Wabarakatuh,</p>

                    <p>Dear {attendee.first_name},</p>

                    <p>We extend our heartfelt appreciation for your active participation in the Dawrah program.</p>

                    <p>The Dawrah exam is a crucial part of this enriching experience. We are pleased to inform you that the exam link is included below. However, please note that the exam is not open yet. The access to the exam will be activated when we are ready to begin.</p>

                    <p>Thank you for your understanding and commitment to the program. We look forward to your successful completion of the exam.</p>

                    <p>Best regards,</p>
                    <p>The Dawrah Committee</p>

                    <p>Exam Link: <a href="https://forms.gle/STaEMN3fqx3dEhWi9">Click here</a></p>
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
