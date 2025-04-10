# Generated by Django 4.2.20 on 2025-04-03 15:45

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Articles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('state', models.CharField(choices=[('Open', 'Offen'), ('Purchased', 'Gekauft'), ('Cancelled', 'Abgebrochen')], default='Open', max_length=20)),
                ('sum', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='BoughtArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(default=1)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Articles.article')),
                ('basket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bought_articles', to='Baskets.basket')),
            ],
        ),
    ]
