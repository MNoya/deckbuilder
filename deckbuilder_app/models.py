from collections import defaultdict

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from deckbuilder_app.constants import RARITIES, CARD_TYPES, RACES
from deckbuilder_app.user_model import User


class Card(models.Model):
    name = models.CharField(max_length=50)
    cost = models.PositiveSmallIntegerField()
    rarity = models.IntegerField(choices=[(i, name) for i, name in enumerate(RARITIES)], default=RARITIES[0])
    card_type = models.IntegerField(choices=[(i, name) for i, name in enumerate(CARD_TYPES)], default=CARD_TYPES[0])
    race = models.IntegerField(choices=[(i, name) for i, name in enumerate(RACES)], default=RACES[0])
    attack = models.PositiveSmallIntegerField(null=True, blank=True)
    defense = models.PositiveSmallIntegerField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    art = models.ImageField(upload_to='cards', null=True, blank=True)

    fields = ['name', 'race', 'cost', 'text', 'card_type', 'rarity', 'attack', 'defense']
    order_by_fields = ['cost', '-rarity', '-race', '-card_type', 'name']

    class Meta:
        db_table = 'card'
        unique_together = ('name', 'race', 'rarity')

    def __str__(self):
        return self.name

    @staticmethod
    def get_all_cards():
        return Card.objects.all().order_by(*Card.order_by_fields)


class Deck(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    cards = models.ManyToManyField(Card, through='CardInDeck')
    time_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    # TODO: PvP/Galaxy-specific
    # TODO: Creator Notes
    # TODO: User Likes
    # TODO: User Comments on Deck (and Answers from Creator)
    # TODO: Cost Mana-Curve Graph
    # TODO: Sample Hand generator

    class Meta:
        db_table = 'deck'

    def __str__(self):
        return self.name

    def get_decklist(self):
        result = []
        for card in self.cards.all().order_by(*Card.order_by_fields):
            result += card.name
        return result

    def get_deck_races(self):
        # First race is the one with more cards
        deck_races = defaultdict(int)
        for card_in_deck in self.cardindeck_set.all():
            deck_races[card_in_deck.card.race] += card_in_deck.copies
        sorted_races = sorted(dict(deck_races), key=deck_races.get, reverse=True)
        return [(race, deck_races[race]) for race in sorted_races]


class CardInDeck(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    copies = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(3), MinValueValidator(1)])

    order_by_fields = ['card__cost', '-card__rarity', '-card__race', '-card__card_type', 'card__name']

    class Meta:
        db_table = 'card_in_deck'
        unique_together = ('card', 'deck')
