from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import EmailCheckSerializer, LoginSerializer, RegistrationSerializer


User = get_user_model()


class RegistrationView(generics.CreateAPIView):
    """API view for user registration."""

    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """Handle user registration and return auth data."""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user_id": user.id,
                "email": user.email,
                "fullname": user.fullname,
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    """API view for user login."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticate user and return auth token."""

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user_id": user.id,
                "email": user.email,
                "fullname": user.fullname,
            },
            status=status.HTTP_200_OK
        )


class EmailCheckView(APIView):
    """API view to check if an email exists."""

    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Return user data if email exists."""
        
        serializer = EmailCheckSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Email not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response (
            {
                "id": user.id,
                "email": user.email,
                "fullname": user.fullname,
            },
            status=status.HTTP_200_OK
        )