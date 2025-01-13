import os
from django.core.management.base import BaseCommand

from bot.my_bot import main

class Command(BaseCommand):
    help = 'Запуск бота'

    def handle(self, *args, **options):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'books.settings')
        main()