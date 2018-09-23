from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class UsernameAuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)
        return user


class EmailAuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
            if user.check_password(raw_password=password):
                return user
            return None
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None