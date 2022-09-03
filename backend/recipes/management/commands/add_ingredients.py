import codecs
import csv
import os

from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredients


class Command(BaseCommand):

    help = 'Adding Ingredients'

    def handle(self, *args, **options):
        with open(
                  os.path.join(
                    BASE_DIR, 'data/ingredients.csv'), 'rb')as csv_file:
            csv_reader = csv.reader((
                codecs.iterdecode(csv_file, 'utf-8')), delimiter=';')
            for row in csv_reader:
                row_split = row[0].split(',')
                Ingredients.objects.create(
                    name=row_split[0], measurement_unit=row_split[1])
        print('Игридиенты добавлены')
