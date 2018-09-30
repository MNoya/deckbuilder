from django import forms
from deckbuilder_app.models import *


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'avatar')


class RegisterForm(forms.Form):
    """
    Form used to register a new user
    """
    username = forms.CharField(max_length=40, required=True)
    email = forms.EmailField()
    password = forms.CharField(required=True, widget=forms.PasswordInput())
    # password_confirmation = forms.CharField(widget=forms.PasswordInput(), required=True, label="Confirm password")
    #
    # def clean(self):
    #     cleaned_data = super(RegisterForm, self).clean()
    #     password = cleaned_data.get("password")
    #     confirm_password = cleaned_data.get("password_confirmation")
    #
    #     if password != confirm_password:
    #         raise forms.ValidationError("Passwords do not match")


class ResetPasswordForm(forms.Form):
    """
    Form used to reset password
    """
    token = forms.CharField(widget=forms.HiddenInput())
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirmation = forms.CharField(widget=forms.PasswordInput())

    def is_valid(self):
        valid = super(ResetPasswordForm, self).is_valid()
        return valid and self.cleaned_data.get('password') == self.cleaned_data.get('password_confirmation')


class RequestResetPasswordForm(forms.Form):
    """
    Request a password reset form
    """
    email_or_username = forms.CharField(required=True)

    def clean(self):
        cleaned_data = super(RequestResetPasswordForm, self).clean()
        email_or_username = cleaned_data.get("email_or_username")
        # Find User with the email or the username
        try:
            user = User.objects.get(username=email_or_username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=email_or_username)
            except User.DoesNotExist:
                raise forms.ValidationError("Email not found")
        cleaned_data['email'] = user.email

    def is_valid(self):
        valid = super(RequestResetPasswordForm, self).is_valid()
        if valid:
            self.cleaned_data['email'] = self.cleaned_data['email'].lower()
        return valid
