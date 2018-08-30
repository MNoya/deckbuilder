import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView

from deckbuilder_app.constants import RACES
from deckbuilder_app.forms import UserProfileForm, RegisterForm, ResetPasswordForm
from deckbuilder_app.models import Deck, Card, CardInDeck
from deckbuilder_app.user_model import User, EmailToken

import deckbuilder_app.errors as err

log = logging.getLogger(__name__)

GET = 'GET'
POST = 'POST'

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
        form = ResetPasswordForm(initial={'token': token})
        return render(request, 'views/reset_password.html', {'form': form})
    # POST request
    elif request.POST:
        template = 'views/validation_template.html'
        context = {'title': 'Success', 'message': 'Your password was changed.'}
        # get data from form and reset password
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            token_value = form.cleaned_data.get('token')
            updated, errors = User.update_password(token_value, form.cleaned_data.get('password1'))
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
        "userTechnologies": user.technologies.all(),
        "average_score_as_coder": request.user.get_coder_score(),
        "average_score_as_po": request.user.get_owner_score(),
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
        "profileTechnologies": user.technologies.all(),
        "average_score_as_coder": user.get_coder_score(),
        "average_score_as_po": user.get_owner_score(),
    }
    return render(request, 'views/user_profile.html', context)


##########

class DeckListView(ListView):
    model = Deck
    template_name = 'deck_list.html'

    def get_context_data(self, **kwargs):
        context = super(DeckListView, self).get_context_data(**kwargs)
        # context['total_time_played'] = Match.objects.aggregate(Sum('duration'))['duration__sum']
        return context

    def get_template_names(self):
        return self.template_name


class DeckDetailView(DetailView):
    model = Deck
    template_name = 'deck_detail.html'

    def get_context_data(self, **kwargs):
        context = super(DeckDetailView, self).get_context_data(**kwargs)
        context['card_count'] = 0
        context['cards'] = context['object'].cardindeck_set.all().order_by(*CardInDeck.order_by_fields)
        for card_in_deck in context['cards']:
            context['card_count'] += card_in_deck.copies
        return context


class CardDetailView(DetailView):
    model = Card
    template_name = 'card_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CardDetailView, self).get_context_data(**kwargs)
        context['decks'] = []
        return context


def deck_edit(request, pk):
    # TODO: Only deck creator can edit it
    template_name = 'deck_edit.html'
    deck = Deck.objects.get(pk=pk)

    if request.POST:
        log.info("Updating deck '{}' id {}".format(deck.name, deck.pk))
        deck_data = json.loads(request.body)
        log.debug("Request data: {}".format(deck_data))
        name = deck_data['name']
        if name != deck.name:
            log.info("Updating name to '{}'".format(name))
            deck.name = name
            deck.save()
        cards_data = deck_data['cards']
        updated_cards = set(cards_data.keys())
        current_cards = set(deck.cards.values_list('name', flat=True))
        removed_cards = []
        for card_name, number in cards_data.items():
            if number == 0:
                removed_cards.append(card_name)
                updated_cards.remove(card_name)
        added_cards = updated_cards - current_cards
        log.info("Removed cards: {}".format(removed_cards))
        log.info("Added cards: {}".format(added_cards))
        for card_name, number in cards_data.items():
            try:
                card = Card.objects.get(name=card_name)
            except Card.DoesNotExist:
                log.error("Card Does Not Exist: {}".format(card_name))
                continue
            try:
                if card_name in added_cards:
                    CardInDeck.objects.create(deck=deck, card=card, copies=number)
                elif card_name in removed_cards:
                    CardInDeck.objects.get(deck=deck, card=card).delete()
                else:
                    card_in_deck = CardInDeck.objects.get(deck=deck, card=card)
                    if card_in_deck.copies != number:
                        log.info("Updating copies of '{}' from {} to {}".format(card.name, card_in_deck.copies, number))
                        card_in_deck.copies = number
                        card_in_deck.save()
            except Exception:
                log.exception("Problem updating card '{}'".format(card_name))

        return JsonResponse({"message": reverse('deck_detail', kwargs={'pk': deck.pk})})
    else:
        fields = Card.fields
        card_list = []
        for card in Card.get_all_cards():
            card_data = {}
            for field in fields:
                card_data[field] = getattr(card, field)
            if card.art:
                card_data['art'] = str(card.art.url)
            card_list.append(card_data)

        deck_cards = {}
        for card_in_deck in deck.cardindeck_set.all().order_by(*CardInDeck.order_by_fields):
            deck_cards[card_in_deck.card.name] = card_in_deck.copies

        return render(request,
                      template_name=template_name,
                      context={
                          'deck_id': deck.pk,
                          'races': [[i, race_name] for i, race_name in enumerate(RACES)],
                          'cards': json.dumps(card_list),
                          'deck_cards': json.dumps(deck_cards),
                          'deck_name': deck.name
                      })


def new_deck(request):
    template_name = 'new_deck.html'

    if request.POST:
        deck_data = json.loads(request.body)
        log.info("Create New Deck: {}".format(deck_data))
        new_deck = Deck.objects.create(name=deck_data['name'])

        for card_name, number in deck_data['cards'].items():
            try:
                card = Card.objects.get(name=card_name)
            except Card.DoesNotExist:
                log.error("Card Does Not Exist: {}".format(card_name))

            CardInDeck.objects.create(deck=new_deck, card=card, copies=number)

        return JsonResponse({"message": reverse('deck_detail', kwargs={'pk': new_deck.pk})})
    else:
        fields = Card.fields
        card_list = []
        for card in Card.get_all_cards():
            card_data = {}
            for field in fields:
                card_data[field] = getattr(card, field)
            if card.art:
                card_data['art'] = str(card.art.url)
            card_list.append(card_data)

        return render(request,
                      template_name=template_name,
                      context={
                          'races': [[i, race_name] for i, race_name in enumerate(RACES)],
                          'cards': json.dumps(card_list)
                      })
