import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse

import deckbuilder_app.errors as err
from deckbuilder_app.constants import GET, POST
from deckbuilder_app.forms import UserProfileForm, RegisterForm, ResetPasswordForm, RequestResetPasswordForm
from deckbuilder_app.user_model import User, EmailToken

log = logging.getLogger(__name__)


def register(request):
    """
    View used to register a new user
    :param request:
    """
    if request.method == GET:
        # create form to render and return it
        form = RegisterForm()
        return render(request, 'views/register.html', {'form': form})
    elif request.method == POST:
        # create form from request POST params
        form = RegisterForm(request.POST)
        template = 'views/validation_template.html'
        context = {'title': 'Success', 'message': 'Great! Your account was created, now please check your email to '
                                                  'activate your account.'}
        # check if the form is valid
        if form.is_valid():
            # try to create an user
            form.cleaned_data.pop('password_confirmation')
            user, errors = User.register(**form.cleaned_data)
            if user:
                # render success
                return render(request, template, context)
            else:
                # show errors and redirect to register form
                for error in errors:
                    messages.error(request, error.text)
                return redirect(reverse('register'))
        else:
            # show errors and redirect to form
            messages.error(request, 'Invalid form data')
            response = redirect(reverse('register'))
        return response


def recover_password(request):
    """
    View to ask for the mail in the case the user wants to change his password
    :param request: Django request object
    :return: HTML template
    """
    # GET requests
    if request.method == GET:
        # render page with reset password form
        form = RequestResetPasswordForm()
        return render(request, 'views/password_recovery.html', {'form': form})
    # POST request
    elif request.method == POST:
        form = RequestResetPasswordForm(request.POST)
        if form.is_valid():
            reset_email = form.cleaned_data['email']
            user = User.get_user_by_email(reset_email)
            if user:
                user.recover_password()
                template = 'views/validation_template.html'
                context = {'title': 'Success',
                           'message': 'Great %s! Now please check your email to '
                                      'reset your password.' % user.username}
                return render(request, template, context)
            else:
                messages.error(request, 'Email not found')
                return redirect(reverse('reset_password_form'))
        else:
            # show errors and redirect to form
            messages.error(request, 'Invalid form data')
            response = redirect(reverse('reset_password_form'))
        return response


def reset_password(request, token=None):
    """
    View used to reset password
    :param request: Django request object
    :param token: Token object used to validate password reset
    :return: HTML template
    """
    # GET requests
    if request.method == GET:
        # render page with reset password form
        form = ResetPasswordForm()
        return render(request, 'views/password_reset.html', {'form': form, 'token': token})
    # POST request
    elif request.POST:
        template = 'views/validation_template.html'
        context = {'title': 'Success', 'message': 'Your password was changed.'}
        # get data from form and reset password
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            token_value = form.cleaned_data.get('token')
            updated, errors = User.update_password(token_value, form.cleaned_data.get('password'))
            if updated:
                # password was updated
                response = render(request, template, context)
            else:
                # show errors and redirect to form
                for error in errors:
                    messages.error(request, error.text)
                response = redirect(reverse('reset_password_get', args=[request.POST.get('token', '')]))
        else:
            # show errors and redirect to form
            messages.error(request, err.Error(err.ERROR_RESET_PASSWORD_NOT_MATCH).text)
            response = redirect(reverse('reset_password_get', args=[request.POST.get('token', '')]))
        return response


def verify_registration_token(token):
    error = ''
    verified = False

    try:
        with transaction.atomic():
            token_obj = EmailToken.objects.select_related('user').get(value=token)
            if token_obj.is_valid():
                token_obj.user.is_active = True
                token_obj.user.save()
                token_obj.delete()
                verified = True
            else:
                error = err.Error(err.ERROR_TOKEN_NOT_VALID)
    except EmailToken.DoesNotExist:
        error = err.Error(err.ERROR_TOKEN_NOT_FOUND)
    except Exception as e:
        error = err.Error(err.ERROR_UNKNOWN)

    return verified, error


def validate_email(request, token):
    verified, error = verify_registration_token(token)
    template = 'views/validation_template.html'

    if verified:
        msg = "This process was done correctly."
        return render(request, template, {'title': 'Success!', 'message': msg})
    else:
        return render(request, template, {'title': 'Ops!, error:', 'message': error.text})


##########

@login_required
def my_profile(request):
    form = UserProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    user = request.user
    context = {
        "form": form,
    }
    if request.method == GET:
        return render(request, 'views/my_profile.html', context)
    elif request.POST:
        if form.is_valid():
            log.info("Updating user {}".format(request.user.username))
            form.save()
            messages.success(request, 'User updated successfully')
            return redirect(reverse('my_profile'))
        else:
            log.error("Invalid form data: {}".format(form.errors.as_json()))
            messages.error(request, 'Invalid form data')

    return render(request, 'views/my_profile.html', context)


@login_required
def user_profile(request, pk):
    user = User.objects.get(pk=pk)

    context = {
        "profile": user,
    }
    return render(request, 'views/user_profile.html', context)
