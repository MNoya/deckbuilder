import csv
import os

from django.conf import settings

from deckbuilder_app.models import GalaxyMap, Card


def update_galaxy():
    print("=" * 60)
    print("Updating Galaxy Maps...")
    final_maps = load_galaxy_csv('Galaxy Maps - Final Missions.csv')
    normal_maps = load_galaxy_csv('Galaxy Maps - Missions.csv')

    final_map_names = update_galaxy_maps(final_maps, is_final=True)
    mission_map_names = update_galaxy_maps(normal_maps)

    all_map_names = final_map_names + mission_map_names
    for galaxy_map in GalaxyMap.objects.all():
        if galaxy_map.name not in all_map_names:
            galaxy_map.delete()

    print("Finished updating Galaxy Maps")


def update_galaxy_maps(map_list, is_final=False):
    map_names = []
    for map_data in map_list:
        map_name = map_data.pop('name')
        map_names.append(map_name)
        if map_data.get('card_names'):
            cards_in_map = map_data.pop('card_names')
        else:
            cards_in_map = []

        map, created = GalaxyMap.objects.update_or_create(name=map_name, is_final=is_final, defaults={**map_data})
        if not created:
            print("Updating Galaxy Map '{}'".format(map_name))
            for card in map.cards.all():
                if card.name not in cards_in_map:
                    map.cards.remove(card)
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
                continue
            except Card.MultipleObjectsReturned:
                card = Card.objects.filter(name=card_name).first()
                map.cards.add(card)
                print("\tWARN: Multiple cards match name '{}', adding the first one: Race {} Cost {}".
                      format(card_name, card.get_race_display(), card.cost))

    return map_names


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
                'difficulty': row[2],
                'notes': row[3],
                'campaign': row[4]
            }
            if row[1]:
                map_data['card_names'] = [card_name.strip() for card_name in row[1].split(card_splitter)]

            result.append(map_data)
    return result
