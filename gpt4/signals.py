import os

from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage

from gpt4.models import BookG


@receiver(post_delete, sender=BookG)
def delete_book_cover(sender, instance, **kwargs):
    """Автоматически удаляет изображение из хранилища при удалении обьекта BookG"""
    if instance.cover and instance.cover.name:  # Проверяем, что поле не пустое
        cover_path = instance.cover.path
        if os.path.exists(cover_path):  # Проверяем, существует ли файл
            default_storage.delete(cover_path)
