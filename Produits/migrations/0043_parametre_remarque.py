# Generated by Django 5.1.4 on 2025-01-27 23:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Produits', '0042_categories_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='parametre',
            name='remarque',
            field=models.TextField(blank=True, default='Les produits vendus ne sont ni échangés ni remboursés. Pour tout soucis, voir le vendeur.', max_length=500, null=True),
        ),
    ]
