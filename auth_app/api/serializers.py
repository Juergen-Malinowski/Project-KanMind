from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers


User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, min_length=8)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "fullname", "password", "repeated_password"]

    def validate_email(self, value):
        """Validate that the email is unique and normalized."""
        email = value.lower()

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return email

    def validate(self, attrs):
        """Validate that both password fields match."""

        password = attrs.get("password")
        repeated_password = attrs.get("repeated_password")

        if password != repeated_password:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """Create and return a new user instance."""

        validated_data.pop("repeated_password")

        return User.objects.create_user(
            email=validated_data["email"],
            fullname=validated_data["fullname"],
            password=validated_data["password"],
        )


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate user credentials."""
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            username=email,
            password=password
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid email or password."
            )
        
        if not user.is_active:
            raise serializers.ValidationError(
                "User account is disabled."
            )

        attrs["user"] = user
        return attrs


class EmailCheckSerializer(serializers.Serializer):
    """Serializer for email existence check."""

    email = serializers.EmailField()

    def validate_email(self, value):
        """Normalize email to lowercase."""

        return value.lower()