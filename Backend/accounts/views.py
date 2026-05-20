from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailVerificationSerializer,
    ResendVerificationEmailSerializer,
)


User = get_user_model()



class RegisterView(APIView):
    """
    API view for user registration.
    Accepts POST request with username, email, and password.
    Returns access and refresh tokens on successful registration.
    Sends verification email to the user.
    """

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            
            # Send verification email
            self._send_verification_email(user, request)
            
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "User registered successfully. Please verify your email.",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _send_verification_email(user, request):
        """Send verification email to the user."""
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_path = getattr(settings, "EMAIL_VERIFICATION_URL", "/verify-email/")
        verify_link = f"{request.build_absolute_uri('/').rstrip('/')}{verification_path}?uid={uid}&token={token}"

        subject = "Verify your email"
        message = (
            f"Hello {user.username or user.email},\n\n"
            f"Click this link to verify your email:\n{verify_link}\n\n"
            "If you did not sign up, you can ignore this email."
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )



class LoginView(APIView):
    """
    API view for user login.
    Accepts POST request with email and password.
    Returns access and refresh tokens on successful authentication.
    """

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request, username=email, password=password)

        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )



class ChangePasswordView(APIView):
    """
    API view for changing user password.
    Requires authentication.
    Accepts POST request with old_password and new_password.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=PasswordChangeSerializer, security=[{"Bearer": []}])
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(old_password):
            return Response(
                {"old_password": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password updated successfully."},
            status=status.HTTP_200_OK
        )


class PasswordResetRequestView(APIView):
    """
    Starts the password reset flow by sending a reset link to the user's email.
    """

    @swagger_auto_schema(request_body=PasswordResetRequestSerializer)
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                {"message": "If an account exists for that email, a reset link has been sent."},
                status=status.HTTP_200_OK,
            )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_path = getattr(settings, "PASSWORD_RESET_CONFIRM_URL", "/reset-password/confirm/")
        reset_link = f"{request.build_absolute_uri('/').rstrip('/')}{reset_path}?uid={uid}&token={token}"

        subject = "Password reset request"
        message = (
            f"Hello {user.username or user.email},\n\n"
            f"Use this link to reset your password:\n{reset_link}\n\n"
            "If you did not request this, you can ignore this email."
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {"message": "If an account exists for that email, a reset link has been sent."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    """
    Completes the password reset flow using a uid/token pair.
    """

    @swagger_auto_schema(request_body=PasswordResetConfirmSerializer)
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"detail": "Invalid reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired reset token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return Response(
            {"message": "Password reset successfully."},
            status=status.HTTP_200_OK,
        )


class EmailVerifyView(APIView):
    """
    API view to verify user email using uid and token.
    Accepts GET or POST request with uid and token parameters.
    """

    @swagger_auto_schema(
        request_body=EmailVerificationSerializer,
        responses={200: openapi.Response("Email verified successfully.")}
    )
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"detail": "Invalid verification link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired verification token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_email_verified:
            return Response(
                {"message": "Email already verified."},
                status=status.HTTP_200_OK,
            )

        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

        return Response(
            {"message": "Email verified successfully."},
            status=status.HTTP_200_OK,
        )


class ResendVerificationEmailView(APIView):
    """
    API view to resend verification email to user.
    Accepts POST request with email.
    """

    @swagger_auto_schema(request_body=ResendVerificationEmailSerializer)
    def post(self, request):
        serializer = ResendVerificationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                {"message": "If an account exists for that email, a verification email has been sent."},
                status=status.HTTP_200_OK,
            )

        if user.is_email_verified:
            return Response(
                {"message": "Email is already verified."},
                status=status.HTTP_200_OK,
            )

        # Send verification email
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_path = getattr(settings, "EMAIL_VERIFICATION_URL", "/verify-email/")
        verify_link = f"{request.build_absolute_uri('/').rstrip('/')}{verification_path}?uid={uid}&token={token}"

        subject = "Verify your email"
        message = (
            f"Hello {user.username or user.email},\n\n"
            f"Click this link to verify your email:\n{verify_link}\n\n"
            "If you did not request this, you can ignore this email."
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {"message": "If an account exists for that email, a verification email has been sent."},
            status=status.HTTP_200_OK,
        )
