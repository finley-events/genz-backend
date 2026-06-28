# users/managers.py

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom manager for the User model.
    """

    use_in_migrations = True

    def create_user(
        self,
        email: str,
        username: str,
        phone_number: str,
        password: str | None = None,
        **extra_fields,
    ):
        """
        Create and return a regular user.
        """
        if not email:
            raise ValueError("An email address is required.")

        if not username:
            raise ValueError("A username is required.")

        if not phone_number:
            raise ValueError("A phone number is required.")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            username=username,
            phone_number=phone_number,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email: str,
        username: str,
        phone_number: str,
        password: str,
        **extra_fields,
    ):
        """
        Create and return a superuser.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            email=email,
            username=username,
            phone_number=phone_number,
            password=password,
            **extra_fields,
        )
