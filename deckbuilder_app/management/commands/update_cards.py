from django.core.management.base import BaseCommand, CommandError

from deckbuilder_app.scripts.update_cards import update_cards


class Command(BaseCommand):
    help = 'Updates cards based on stored csv data'

    def add_arguments(self, parser):
        parser.add_argument('--race', nargs='+', type=int)

    def handle(self, *args, **options):
        update_cards()