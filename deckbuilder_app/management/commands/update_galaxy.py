from django.core.management.base import BaseCommand, CommandError

from deckbuilder_app.scripts.update_galaxy import update_galaxy


class Command(BaseCommand):
    help = 'Updates galaxy maps based on stored data'

    def handle(self, *args, **options):
        update_galaxy()
