# Generated by Django 5.1.2 on 2024-10-25 07:52

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0001_initial'),
        ('ratings', '0007_alter_ratings_restaurant_review'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExploreHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clicked_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='menu_history', to='ratings.menu')),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='explore_history', to='authentication.userprofile')),
            ],
        ),
    ]