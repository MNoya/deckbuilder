import csv
import os

from django.conf import settings

from deckbuilder_app.models import GalaxyMap, Card


def update_galaxy():
    print("=" * 60)
    print("Updating Galaxy Maps...")
    final_maps = load_galaxy_csv('Galaxy Maps - Final Missions.csv')
    normal_maps = load_galaxy_csv('Galaxy Maps - Missions.csv')

    update_galaxy_maps(final_maps, is_final=True)
    update_galaxy_maps(normal_maps)

    print("Finished updating Galaxy Maps")


def update_galaxy_maps(map_list, is_final=False):
    for map_data in map_list:
        map_name = map_data.pop('name')

        if map_data.get('card_names'):
            cards_in_map = map_data.pop('card_names')
        else:
            cards_in_map = []


        map, created = GalaxyMap.objects.get_or_create(name=map_name, is_final=is_final, defaults={**map_data})
        if not created:
            print("Updating Galaxy Map '{}'".format(map_name))
        else:
            print("Creating Galaxy Map '{}'".format(map_name))

        # Populate cards
        for card_name in cards_in_map:
            try:
                card = Card.objects.get(name=card_name)
                map.cards.add(card)
                print("\tAdded '{}'".format(card.name, map.name))
            except Card.DoesNotExist:
                print("\tERROR: Card '{}' does not exist, could not be added".format(card_name, map_name))


def load_galaxy_csv(file_name):
    card_splitter = '|' # To avoid mistakes with commas in card names
    path = os.path.join(settings.BASE_DIR, 'deckbuilder_app', 'data', file_name)
    result = []
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"', lineterminator='\n')
        next(reader, None)
        for row in reader:
            map_data = {
                'name': row[0],
                'notes': row[3],
                'campaign': row[4]
            }
            if row[1]:
                map_data['card_names'] = [card_name.strip() for card_name in row[1].split(card_splitter)]
            if row[2]:
                map_data['difficulty'] = [difficulty_name.strip() for difficulty_name in row[2].split(',')]

            result.append(map_data)
    return result
