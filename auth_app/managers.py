from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Manager for custom user model."""

    def create_user(self, email, fullname, password=None, **extra_fields):
        """Create and return a regular user."""

        if not email:
            raise ValueError("The email field is required.")

        if not fullname:
            raise ValueError("The fullname field is required.")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            fullname=fullname,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, fullname, password=None, **extra_fields):
        """Create and return a superuser."""

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, fullname, password, **extra_fields)
