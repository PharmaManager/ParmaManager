# Generated by Django 5.1.4 on 2025-01-11 09:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Produits', '0027_rename_commande_bondecommande_commandefac'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bondecommande',
            name='fournisseur',
        ),
        migrations.AlterField(
            model_name='commandefact',
            name='fournisseur',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fournisseurs', to='Produits.fournisseur'),
        ),
    ]
