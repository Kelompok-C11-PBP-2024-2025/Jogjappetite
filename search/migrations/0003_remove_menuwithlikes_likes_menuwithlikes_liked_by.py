# Generated by Django 5.1.2 on 2024-10-27 11:52

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0002_menuwithlikes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menuwithlikes',
            name='likes',
        ),
        migrations.AddField(
            model_name='menuwithlikes',
            name='liked_by',
            field=models.ManyToManyField(blank=True, related_name='liked_menus', to=settings.AUTH_USER_MODEL),
        ),
    ]
