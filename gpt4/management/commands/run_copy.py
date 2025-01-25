import os
from django.core.management.base import BaseCommand

from gpt4.dictonary.dict import copy

class Command(BaseCommand):
    help = 'Запуск скрипта текста'

    def handle(self, *args, **options):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'books.settings')
        copy()