from django.db import models
import uuid


class Attendee(models.Model):
    LEVEL_CHOICES = (
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    )
    id = models.UUIDField(unique=True, default=uuid.uuid4, primary_key=True)
    dawrah_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    level_of_study = models.PositiveIntegerField()
    hall_off_residence = models.CharField(max_length=100)
    level = models.CharField(max_length=100, choices=LEVEL_CHOICES)
    paid = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["dawrah_id"]


# class Volunteer(models.Model):
#     pass
