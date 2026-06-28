from django.contrib.auth import get_user_model

from .models import Wallet

User = get_user_model()


class SystemWalletService:
    """
    Handles creation and retrieval of system wallets.
    """

    @staticmethod
    def get_mpesa_wallet():
        user, _ = User.objects.get_or_create(
            username="mpesa_clearing",
            defaults={
                "email": "mpesa@system.local",
                "is_active": False,
            },
        )

        wallet, _ = Wallet.objects.get_or_create(
            user=user,
            defaults={
                "wallet_address": "MPESA_CLEARING",
            },
        )

        return wallet

    @staticmethod
    def get_treasury_wallet():
        user, _ = User.objects.get_or_create(
            username="treasury_wallet",
            defaults={
                "email": "treasury@system.local",
                "is_active": False,
            },
        )

        wallet, _ = Wallet.objects.get_or_create(
            user=user,
            defaults={
                "wallet_address": "TREASURY",
            },
        )

        return wallet

    @staticmethod
    def get_rewards_wallet():
        user, _ = User.objects.get_or_create(
            username="rewards_wallet",
            defaults={
                "email": "rewards@system.local",
                "is_active": False,
            },
        )

        wallet, _ = Wallet.objects.get_or_create(
            user=user,
            defaults={
                "wallet_address": "REWARDS",
            },
        )

        return wallet

    @staticmethod
    def get_campaign_wallet():
        user, _ = User.objects.get_or_create(
            username="campaign_wallet",
            defaults={
                "email": "campaigns@system.local",
                "is_active": False,
            },
        )

        wallet, _ = Wallet.objects.get_or_create(
            user=user,
            defaults={
                "wallet_address": "CAMPAIGN",
            },
        )

        return wallet
