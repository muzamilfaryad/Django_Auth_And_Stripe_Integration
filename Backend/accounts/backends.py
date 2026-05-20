from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        login_value = kwargs.get(UserModel.USERNAME_FIELD) or username or kwargs.get("email")

        if not login_value or password is None:
            return None

        try:
            user = UserModel.objects.get(
                Q(email__iexact=login_value) | Q(username__iexact=login_value)
            )
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None