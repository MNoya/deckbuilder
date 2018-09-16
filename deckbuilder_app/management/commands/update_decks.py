from django.core.management.base import BaseCommand, CommandError

from deckbuilder_app.scripts.update_decks import update_decks


class Command(BaseCommand):
    help = 'Updates default decks based on stored data'

    def add_arguments(self, parser):
        parser.add_argument('--delete', action='store_true', dest='delete',
            help='Delete all admin-created decks',
        )

    def handle(self, *args, **options):
        update_decks(options['delete'])