# Generated by Django 4.2.20 on 2025-04-08 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paypal_link', models.URLField(verbose_name='PayPal-Link')),
                ('bild_links', models.ImageField(upload_to='settings/', verbose_name='Bild links')),
                ('bild_rechts', models.ImageField(upload_to='settings/', verbose_name='Bild rechts')),
                ('beschreibung', models.TextField(blank=True, verbose_name='Beschreibung (optional)')),
            ],
            options={
                'verbose_name': 'Einstellungen',
                'verbose_name_plural': 'Einstellungen',
            },
        ),
    ]
