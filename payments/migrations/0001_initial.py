# Generated by Django 4.2.7 on 2024-12-24 22:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("registration", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EventPayment",
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
                ("reference", models.CharField(max_length=100, unique=True)),
                ("status", models.CharField(max_length=50)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("message", models.CharField(blank=True, max_length=255, null=True)),
                ("paid_at", models.DateTimeField(auto_now_add=True)),
                (
                    "attendee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="registration.attendee",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Donation",
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
                ("reference", models.CharField(max_length=100, unique=True)),
                ("status", models.CharField(max_length=50)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("message", models.CharField(blank=True, max_length=255, null=True)),
                ("paid_at", models.DateTimeField(auto_now_add=True)),
                (
                    "donor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="registration.donor",
                    ),
                ),
            ],
        ),
    ]
