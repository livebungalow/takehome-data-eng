from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Imports data about houses'

    def add_arguments(self, parser):
        # TODO: Add any arguments here
        pass

    def handle(self, *args, **options):
        # TODO: implement your import command
        self.stdout.write("Import to be implemented.")
