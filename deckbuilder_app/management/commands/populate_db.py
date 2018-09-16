from django.core.management.base import BaseCommand, CommandError

from deckbuilder_app.scripts.create_admin_superuser import create_admin_superuser
from deckbuilder_app.scripts.update_cards import update_cards
from deckbuilder_app.scripts.update_decks import update_decks
from deckbuilder_app.scripts.update_galaxy import update_galaxy


class Command(BaseCommand):
    help = 'Populates cards, decks and galaxy maps'

    def handle(self, *args, **options):
        create_admin_superuser()
        update_cards()
        update_decks()
        update_galaxy()
