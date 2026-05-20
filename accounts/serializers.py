from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "username", "email", "password", "first_name", "last_name",
            "phone_number", "date_of_birth", "country", "city", "occupation"
        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for user profile details with all fields."""
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "phone_number", "bio", "profile_picture", "date_of_birth",
            "country", "city", "occupation", "is_email_verified",
            "is_phone_verified", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_email_verified", "is_phone_verified"]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate_new_password(self, value):
        # You can add more complex password validation here if desired
        return value

    def validate(self, attrs):
        """
        Ensure new password is different from old password.
        """
        if attrs.get("new_password") == attrs.get("old_password"):
            raise serializers.ValidationError(
                "New password must be different from the old password."
            )
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()


class ResendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
