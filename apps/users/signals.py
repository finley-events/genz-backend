# users/signals.py

import secrets
import string

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, User

REFERRAL_ALPHABET = string.ascii_uppercase + string.digits
REFERRAL_CODE_LENGTH = 8


def generate_referral_code(length: int = REFERRAL_CODE_LENGTH) -> str:
    """
    Generate a unique referral code.

    Example:
        A7X9P2KD
    """
    while True:
        code = "".join(secrets.choice(REFERRAL_ALPHABET) for _ in range(length))

        if not Profile.objects.filter(referral_code=code).exists():
            return code


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a Profile whenever a new User is created.
    """
    if not created:
        return

    with transaction.atomic():
        Profile.objects.create(
            user=instance,
            display_name=instance.username,
            referral_code=generate_referral_code(),
            badge_level=1,
            reputation_score=0,
        )
