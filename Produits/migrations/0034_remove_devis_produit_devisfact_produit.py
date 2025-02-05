# Generated by Django 5.1.4 on 2025-01-13 23:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Produits', '0033_remove_devisfact_produit_devis_produit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='devis',
            name='produit',
        ),
        migrations.AddField(
            model_name='devisfact',
            name='produit',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Produits.produits'),
            preserve_default=False,
        ),
    ]
