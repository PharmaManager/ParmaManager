# Generated by Django 5.1.4 on 2024-12-14 23:48

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Produits', '0002_vente_facture_alter_facture_client_total_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vente',
            old_name='total_amount',
            new_name='montant_total',
        ),
        migrations.RemoveField(
            model_name='facture_client',
            name='date_achat',
        ),
        migrations.RemoveField(
            model_name='facture_client',
            name='produit',
        ),
        migrations.RemoveField(
            model_name='facture_client',
            name='quantite',
        ),
        migrations.RemoveField(
            model_name='facture_client',
            name='total_amount',
        ),
        migrations.AddField(
            model_name='facture_client',
            name='date_creation',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='facture_client',
            name='montant_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='facture_client',
            name='remise_globale',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='facture_client',
            name='customer',
            field=models.ForeignKey(default='client:', on_delete=django.db.models.deletion.CASCADE, related_name='factures', to='Produits.customer'),
        ),
    ]
