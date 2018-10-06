import json
import logging

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


def deck_edit(request, pk):
    # TODO: Only deck creator can edit it
    template_name = 'views/deck_edit.html'
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
        for card in Card.objects.all():
            card_data = {}
            for field in fields:
                card_data[field] = getattr(card, field)
            if card.art:
                card_data['art'] = str(card.art)
            card_list.append(card_data)

        deck_cards = {}
        for card_in_deck in deck.cardindeck_set.all():
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
    template_name = 'views/new_deck.html'
    exclude_card_names = ['Dragon Descendant, Peng']

    if request.POST:
        deck_data = json.loads(request.body)
        log.info("Create New Deck: {}".format(deck_data))
        new_deck = Deck.objects.create(name=deck_data['name'])

        for card_name, number in deck_data['cards'].items():
            try:
                card = Card.objects.get(name=card_name)
            except Card.DoesNotExist:
                log.error("Card Does Not Exist: {}".format(card_name))
                continue

            CardInDeck.objects.create(deck=new_deck, card=card, copies=number)

        return JsonResponse({"message": reverse('deck_detail', kwargs={'pk': new_deck.pk})})
    else:
        fields = Card.fields
        card_list = []
        for card in Card.objects.all().exclude(name__in=exclude_card_names):
            card_data = {}
            for field in fields:
                card_data[field] = getattr(card, field)
            if card.art:
                card_data['art'] = str(card.art)
                # image_name = card['name'].replace(" ", "_") + ".png";
            card_list.append(card_data)

        return render(request,
                      template_name=template_name,
                      context={
                          'races': [[i, race_name] for i, race_name in enumerate(RACES)],
                          'cards': json.dumps(card_list)
                      })
