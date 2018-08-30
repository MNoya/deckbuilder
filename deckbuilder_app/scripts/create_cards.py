import csv
import logging
import os

from deckbuilder_app.constants import *
from deckbuilder_app.models import *

log = logging.getLogger(__name__)

# Build structure
missing_cards_from_raw_data = []

raw_names = []
file_name = os.path.dirname(__file__) + "/Fist Of Truth - All Cards.csv"

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


Card.objects.all().delete()
for card_data in cards_list:
    try:
        abilities = set()
        card_obj = Card.objects.create(**card_data)
        log.info("Created '{}'".format(card_data['name']))
    except Exception as e:
        log.error("Error creating card {}: {}".format(card_data['name'], str(e)))

log.info("Finished creating cards.")
if error_lines:
    log.error("Errors:")
    for line_n, row in error_lines.items():
        log.error("  Line {}: {}".format(line_n, row))
