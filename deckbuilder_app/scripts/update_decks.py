import os

from django.conf import settings

from deckbuilder_app.models import *


def update_decks(delete=False):
    print("=" * 60)
    print("Updating Decks...")
    decks_dir = os.path.join(settings.BASE_DIR, 'deckbuilder_app', 'data', 'decks')
    decks = os.listdir(decks_dir)
    paths = [os.path.join(decks_dir, deck_name) for deck_name in decks]
    user = User.objects.filter(is_superuser=True).first()   # The Admin user
    if delete:
        Deck.objects.filter(user=user).delete()

    for path in paths:
        deck_name = path.split("/")[-1:][0]
        if "." in deck_name:
            deck_name = deck_name.split(".")[0]
        deck, created = Deck.objects.get_or_create(name=deck_name, user=user)
        if not created:
            deck.cardindeck_set.all().delete()
            print("Updating Deck '{}'".format(deck_name))
        else:
            print("Creating Deck '{}'".format(deck_name))
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
                    print("ERROR: Could not add card to deck: '{}' - {}".format(name, e))

    print("Finished updating Decks")
