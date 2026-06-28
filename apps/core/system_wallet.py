from django.contrib.auth import get_user_model

from apps.wallets.models import Wallet

User = get_user_model()


def get_system_wallet():
    system_user = User.objects.get(username="system")

    return Wallet.objects.get(user=system_user)
