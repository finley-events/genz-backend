# apps/wallets/signals.py

import uuid
from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.models import User

from .models import Wallet, WalletBalance


def generate_wallet_address() -> str:
    """
    Generate a unique wallet address.
    Example:
        GZ-8F3A91B4C7D2E5F6
    """
    return f"GZ-{uuid.uuid4().hex[:16].upper()}"


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance: User, created: bool, **kwargs):
    """
    Automatically create a wallet and cached balance
    for every newly registered user.
    """
    if not created:
        return

    wallet = Wallet.objects.create(
        user=instance,
        wallet_address=generate_wallet_address(),
    )

    WalletBalance.objects.create(
        wallet=wallet,
        available_balance=Decimal("0"),
        locked_balance=Decimal("0"),
    )
