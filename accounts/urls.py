from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    ChangePasswordView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    EmailVerifyView,
    ResendVerificationEmailView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('reset-password/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('reset-password/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('verify-email/', EmailVerifyView.as_view(), name='verify-email'),
    path('resend-verification-email/', ResendVerificationEmailView.as_view(), name='resend-verification-email'),
]
