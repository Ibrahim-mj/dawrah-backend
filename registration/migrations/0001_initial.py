# Generated by Django 4.2.7 on 2024-12-24 22:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Attendee",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "dawrah_id",
                    models.CharField(
                        blank=True, max_length=100, null=True, unique=True
                    ),
                ),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=100)),
                ("phone", models.CharField(max_length=100)),
                ("department", models.CharField(max_length=100)),
                ("level_of_study", models.PositiveIntegerField()),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("beginner", "Beginner"),
                            ("intermediate", "Intermediate"),
                            ("advanced", "Advanced"),
                        ],
                        max_length=100,
                    ),
                ),
                ("paid", models.BooleanField(default=False)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["dawrah_id"],
            },
        ),
        migrations.CreateModel(
            name="Donor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=100)),
                ("phone", models.CharField(max_length=100)),
                ("amount", models.PositiveIntegerField()),
                ("donated", models.BooleanField(default=False)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
