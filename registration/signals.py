from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import datetime

from .models import Attendee


def get_last_id():
    """
    Returns the Dawrah ID of the last attendee in the database, or None if there are no attendees.
    """
    last_attendee = Attendee.objects.all().last()
    return last_attendee.dawrah_id if last_attendee else None


@receiver(pre_save, sender=Attendee)
def generate_unique_id(sender, instance, **kwargs):
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
            new_id = "DWR-" + str(new_id).zfill(4)
        else:
            new_id = "DWR-" + str(current_year).zfill(2) + "01"
        instance.dawrah_id = new_id
