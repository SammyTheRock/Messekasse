# Generated by Django 4.2.20 on 2025-04-03 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Baskets', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='boughtarticle',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
