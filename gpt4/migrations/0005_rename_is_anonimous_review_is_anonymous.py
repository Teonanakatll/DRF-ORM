# Generated by Django 5.1.4 on 2024-12-15 17:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gpt4', '0004_genre_author_age_bookg_pages_review_created_at_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='is_anonimous',
            new_name='is_anonymous',
        ),
    ]