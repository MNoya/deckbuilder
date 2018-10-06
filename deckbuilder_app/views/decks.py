import json
import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, DetailView

from deckbuilder_app.constants import RACES
from deckbuilder_app.models import Deck, Card, CardInDeck

log = logging.getLogger(__name__)


def index(request):
    template_name = 'views/index.html'
    return render(request, template_name, context={'decks': Deck.objects.all()[:6]})


class DeckListView(ListView):
    model = Deck
    template_name = 'views/deck_list.html'

    def get_context_data(self, **kwargs):
        context = super(DeckListView, self).get_context_data(**kwargs)
        # context['total_time_played'] = Match.objects.aggregate(Sum('duration'))['duration__sum']
        return context

    def get_template_names(self):
        return self.template_name


class DeckDetailView(DetailView):
    model = Deck
    template_name = 'views/deck_detail.html'

    def get_context_data(self, **kwargs):
        context = super(DeckDetailView, self).get_context_data(**kwargs)
        context['card_count'] = 0
        context['cards'] = context['object'].cardindeck_set.all()
        for card_in_deck in context['cards']:
            context['card_count'] += card_in_deck.copies
        return context


class CardDetailView(DetailView):
    model = Card
    template_name = 'views/card_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CardDetailView, self).get_context_data(**kwargs)
        context['decks'] = []
        return context


def new_deck(request):
    template_name = 'views/deckbuilder.html'

    if request.POST:
        deck_data = json.loads(request.body)
        new_deck = Deck.create(user=request.user, **deck_data)
        return JsonResponse({"message": reverse('deck_detail', kwargs={'pk': new_deck.pk})})
    else:
        context = {
            'races': [[i, race_name] for i, race_name in enumerate(RACES)],
            'cards': json.dumps(Card.cards_list())
        }
        return render(request, template_name=template_name, context=context)


@login_required
def deck_edit(request, pk):
    template_name = 'views/deckbuilder.html'

    deck = Deck.objects.get(pk=pk)
    if request.user != deck.user:
        log.error("User {} tried to edit deck {} of User {} - Forbidden".format(request.user, deck.name, deck.user))
        raise PermissionDenied

    if request.POST:
        deck_data = json.loads(request.body)
        log.info("User {} updating deck {}".format(request.user, deck.name))
        deck.update(deck_data)

        return JsonResponse({"message": reverse('deck_detail', kwargs={'pk': deck.pk})})
    else:
        context = {
            'deck_id': deck.pk,
            'races': [[i, race_name] for i, race_name in enumerate(RACES)],
            'cards': json.dumps(Card.cards_list()),
            'deck_cards': json.dumps(deck.decklist),
            'deck_name': deck.name
        }
        return render(request, template_name=template_name, context=context)
