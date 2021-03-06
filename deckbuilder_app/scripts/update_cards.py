import csv
import logging
import os

from django.conf import settings

from deckbuilder_app.constants import RACES, RARITIES, CARD_TYPES
from deckbuilder_app.models import Card

log = logging.getLogger(__name__)


def update_cards():
    print("=" * 60)
    print("Updating Cards...")
    csv_name = "Fist Of Truth - All Cards.csv"
    file_name = os.path.join(settings.BASE_DIR, "deckbuilder_app", "data", csv_name)

    cards_list = []
    all_names = []
    error_lines = {}

    with open(file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"', lineterminator='\n')
        next(reader, None)
        for row_i, row in enumerate(reader):
            all_names.append(row[0])

            try:
                card_data = {
                    'name': row[0],
                    'race': RACES.index(row[1]),
                    'rarity': RARITIES.index(row[2]),
                    'card_type': CARD_TYPES.index(row[3]),
                    'cost': row[4],
                    'text': row[7]
                }
            except Exception as e:
                error_lines[row_i] = str(e)
                continue

            if row[3] == 'Unit':
                card_data['attack'] = row[5]
                card_data['defense'] = row[6]

            cards_list.append(card_data)

    card_names = []
    missing_cards_art = []
    base_card_path = os.path.join(settings.BASE_DIR, "deckbuilder_app") + settings.STATIC_URL + "img/cards/"
    used_image_names = []
    for card_data in cards_list:
        name = card_data.pop('name')
        race = card_data.pop('race')
        rarity = card_data.pop('rarity')
        try:
            card_names.append(name)
            card_obj, created = Card.objects.update_or_create(name=name, race=race, rarity=rarity,
                                                              defaults={**card_data})
            # Attempt to set card art
            try:
                image_name = card_obj.name.replace(" ", "_") + ".png"
                card_path = "img/cards/" + image_name
                card_media_path = base_card_path + image_name
                if os.path.exists(card_media_path):
                    card_obj.art = card_path
                    card_obj.save()
                    used_image_names.append(image_name)
                else:
                    missing_cards_art.append(card_obj.name)
            except:
                pass

            if created:
                print("Created '{}'".format(name))
            else:
                print("Updated '{}'".format(name))
        except Exception as e:
            print("ERROR creating card {}: {}".format(name, str(e)))

    # Remove cards that have changed names
    for card in Card.objects.all():
        _card_name = card.name
        if _card_name not in card_names:
            card.delete()
            print("Deleted {}".format(_card_name))
        # Remove duplicate cards
        _cards = Card.objects.filter(name=_card_name)
        _cards_count = _cards.count()
        if _cards_count > 1:
            _cards.delete()
            print("WARNING: Deleted {} duplicated cards for name {}".format(_cards_count, _card_name))

    # List unused art
    unused_art = []
    for c in os.listdir(base_card_path):
        if c not in used_image_names:
            unused_art.append(c)

    print("Finished updating Cards")
    if error_lines:
        print("{} Errors:".format(len(error_lines)))
        for line_n, row in error_lines.items():
            print("  Line {}: {}".format(line_n, row))
    if missing_cards_art:
        print("{} Missing Cards Art:".format(len(missing_cards_art)))
        for card_name in missing_cards_art:
            print("  {}".format(card_name))
    if unused_art:
        print("{} Unused images:".format(len(unused_art)))
        for p in unused_art:
            print("\t{}".format(p))
