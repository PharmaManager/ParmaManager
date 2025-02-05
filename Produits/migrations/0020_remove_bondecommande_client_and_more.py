# Generated by Django 5.1.4 on 2025-01-10 12:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Produits', '0019_fournisseur_adress_fournisseur_email_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bondecommande',
            name='client',
        ),
        migrations.AddField(
            model_name='bondecommande',
            name='fournisseur',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='fournisseurs', to='Produits.fournisseur'),
            preserve_default=False,
        ),
    ]
