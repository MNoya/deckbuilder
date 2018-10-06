from collections import defaultdict
from random import sample

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from deckbuilder_app.constants import RARITIES, CARD_TYPES, RACES
from deckbuilder_app.user_model import User, log


class Card(models.Model):
    name = models.CharField(max_length=50)
    cost = models.PositiveSmallIntegerField()
    rarity = models.IntegerField(choices=[(i, name) for i, name in enumerate(RARITIES)], default=RARITIES[0])
    card_type = models.IntegerField(choices=[(i, name) for i, name in enumerate(CARD_TYPES)], default=CARD_TYPES[0])
    race = models.IntegerField(choices=[(i, name) for i, name in enumerate(RACES)], default=RACES[0])
    attack = models.PositiveSmallIntegerField(null=True, blank=True)
    defense = models.PositiveSmallIntegerField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    art = models.CharField(max_length=250, null=True, blank=True)  # static path

    fields = ['name', 'race', 'cost', 'text', 'card_type', 'rarity', 'attack', 'defense', 'art']
    exclude_card_names = ['Dragon Descendant, Peng']

    class Meta:
        db_table = 'card'
        unique_together = ('name', 'race', 'rarity')
        ordering = ['cost', '-rarity', '-race', '-card_type', 'name']

    def __str__(self):
        return self.name

    @classmethod
    def cards_list(cls):
        fields = Card.fields
        card_list = []
        for card in Card.objects.all().exclude(name__in=cls.exclude_card_names):
            card_data = {}
            for field in fields:
                card_data[field] = getattr(card, field)
            card_list.append(card_data)
        return card_list


class Deck(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    cards = models.ManyToManyField(Card, through='CardInDeck')
    time_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    tags = models.ManyToManyField('Tag')

    class Meta:
        db_table = 'deck'
        ordering = ['likes', 'views']

    def __str__(self):
        return self.name

    @property
    def decklist(self):
        """returns dict of card name: copies"""
        result = {}
        for card_in_deck in self.cardindeck_set.all():
            result[card_in_deck.card.name] = card_in_deck.copies
        return result

    @property
    def mana_curve(self):
        """returns dict of cost: copies"""
        result = defaultdict(int)
        for card in self.cardindeck_set.all():
            result[card.cost] += card.copies
        return result

    @property
    def deck_races(self):
        """returns list of tuple (race: number)"""
        # First race is the one with more cards
        deck_races = defaultdict(int)
        for card_in_deck in self.cardindeck_set.all():
            deck_races[card_in_deck.card.race] += card_in_deck.copies
        sorted_races = sorted(dict(deck_races), key=deck_races.get, reverse=True)
        return [(race, deck_races[race]) for race in sorted_races]

    def generate_sample_hand(self):
        """returns a possible starting hand from the deck cards, considering copies"""
        cards = []
        num_starting_cards = 4
        for card_name, copies in self.decklist.items():
            for n in range(copies):
                cards.append(card_name)
        return sample(cards, num_starting_cards)

    def compare_to_deck(self, target_deck):
        """
        Compares this deck to another, returning the difference in each card copies
        :param target_deck: Deck object
        :return: dict of card_name: copies (negative when the card is removed on target_deck)
        """
        result = {}
        compared_decklist = target_deck.decklist

        # Remove cards that dont exist on target deck
        for card, copies in self.decklist.items():
            if compared_decklist.get(card):
                difference = compared_decklist[card] - copies
                if difference:
                    result[card] = difference
            else:
                result[card] = -copies

        # Add new cards from the target deck
        for card, copies in compared_decklist.items():
            if not self.decklist.get(card):
                result[card] = copies
        return result

    def update_owner(self, new_user):
        """
        Change ownership of a deck, for credit purposes
        :param new_user:
        """
        self.user = new_user
        self.save()

    @classmethod
    def create(cls, user, name, cards):
        log.info("Creating New Deck\nName: {}\nUser: {}\nCards: {}".format(name, user, cards))
        if user.is_anonymous:
            new_deck = Deck.objects.create(name=name)
        else:
            new_deck = Deck.objects.create(name=name, user=user)

        for card_name, number in cards.items():
            try:
                card = Card.objects.get(name=card_name)
            except Card.DoesNotExist:
                log.error("Card Does Not Exist: {}".format(card_name))
                continue

            CardInDeck.objects.create(deck=new_deck, card=card, copies=number)
        return new_deck

    def update(self, deck_data):
        log.info("Updating deck '{}' id {}".format(self.name, self.pk))

        # Update deck name
        name = deck_data['name']
        if name != self.name:
            log.info("Updating name to '{}'".format(name))
            self.name = name
            self.save()
        cards_data = deck_data['cards']

        # Add, update or remove cards
        updated_cards = set(cards_data.keys())
        current_cards = set(self.cards.values_list('name', flat=True))
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
                    CardInDeck.objects.create(deck=self, card=card, copies=number)
                elif card_name in removed_cards:
                    CardInDeck.objects.get(deck=self, card=card).delete()
                else:
                    card_in_deck = CardInDeck.objects.get(deck=self, card=card)
                    if card_in_deck.copies != number:
                        log.info("Updating copies of '{}' from {} to {}".format(card.name, card_in_deck.copies, number))
                        card_in_deck.copies = number
                        card_in_deck.save()
            except Exception:
                log.exception("Problem updating card '{}'".format(card_name))


class CardInDeck(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    copies = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(3), MinValueValidator(1)])

    class Meta:
        db_table = 'card_in_deck'
        unique_together = ('card', 'deck')
        ordering = ['card__cost', '-card__rarity', '-card__race', '-card__card_type', 'card__name']

    def __str__(self):
        return "{} {}".format(self.copies, self.card.name)


class Tag(models.Model):
    # TODO: script to create tags
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'tag'
        ordering = ['name']

    def __str__(self):
        return self.name


class GalaxyMap(models.Model):
    name = models.CharField(max_length=50, unique=True)
    cards = models.ManyToManyField(Card)
    difficulty = models.CharField(max_length=30, null=True, blank=True)
    related_decks = models.ManyToManyField('Deck', through='GalaxyDeck')
    notes = models.TextField(null=True, blank=True)
    campaign = models.CharField(max_length=50, null=True, blank=True)
    is_final = models.BooleanField(default=False)

    # TODO: turn order?

    class Meta:
        db_table = 'galaxy_map'
        ordering = ['name', ]

    def __str__(self):
        return "{}".format(self.name)


class GalaxyDeck(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    map = models.ForeignKey(GalaxyMap, on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)

    # winrate?

    class Meta:
        db_table = 'galaxy_deck'
        ordering = ['likes', ]


class DeckComment(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    parent = models.OneToOneField('self', on_delete=models.CASCADE)
    answers = models.ManyToManyField('self')

    class Meta:
        db_table = 'deck_comment'
