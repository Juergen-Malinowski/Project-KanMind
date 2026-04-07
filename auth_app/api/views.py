from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

from .serializers import RegistrationSerializer


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
    pass


class EmailCheckView(APIView):
    pass