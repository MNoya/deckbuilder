import logging
import os

from deckbuilder_app.models import *

log = logging.getLogger(__name__)

base_path = os.path.dirname(__file__)
decks = os.listdir(os.path.join(base_path, 'decks'))
paths = [os.path.join(base_path, 'decks', deck_name) for deck_name in decks]


def create_decks():
    for path in paths:
        deck_name = path.split("/")[-1:][0]
        if "." in deck_name:
            deck_name = deck_name.split(".")[0]
        print("Creating deck {}".format(deck_name))
        deck, created = Deck.objects.get_or_create(name=deck_name, user=User.objects.first())
        if not created:
            deck.cardindeck_set.all().delete()
        with open(path, 'r') as f:
            for line in f:
                line = line.replace('\n', '')
                parts = line.split(' ')
                copies = parts[0]
                name = ' '.join(parts[1:]).strip()
                try:
                    card = Card.objects.get(name__iexact=name)
                    CardInDeck.objects.create(deck=deck, card=card, copies=int(copies))
                except Exception as e:
                    log.error("Problem adding card to deck: '{}' - {}".format(name, e))

create_decks()