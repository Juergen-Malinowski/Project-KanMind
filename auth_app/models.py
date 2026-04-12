from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


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
    

class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model for KanMind."""

    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["fullname"]

    class Meta:
        ordering = ["id"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        """Return string representation of the user."""
        
        return self.email
        


