# Generated by Django 4.2.7 on 2023-11-09 13:24

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("registration", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="attendee",
            options={"ordering": ["dawrah_id"]},
        ),
    ]