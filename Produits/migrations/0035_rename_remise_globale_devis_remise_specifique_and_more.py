# Generated by Django 5.1.4 on 2025-01-14 09:38

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Produits', '0034_remove_devis_produit_devisfact_produit'),
    ]

    operations = [
        migrations.RenameField(
            model_name='devis',
            old_name='remise_globale',
            new_name='remise_specifique',
        ),
        migrations.RenameField(
            model_name='devisfact',
            old_name='remise_specifique',
            new_name='remise_globale',
        ),
        migrations.RemoveField(
            model_name='devis',
            name='client',
        ),
        migrations.RemoveField(
            model_name='devis',
            name='date_creation',
        ),
        migrations.RemoveField(
            model_name='devis',
            name='remarque',
        ),
        migrations.RemoveField(
            model_name='devis',
            name='statut',
        ),
        migrations.RemoveField(
            model_name='devisfact',
            name='prix_unitaire',
        ),
        migrations.RemoveField(
            model_name='devisfact',
            name='produit',
        ),
        migrations.RemoveField(
            model_name='devisfact',
            name='quantite',
        ),
        migrations.RemoveField(
            model_name='devisfact',
            name='sous_total',
        ),
        migrations.AddField(
            model_name='devis',
            name='prix_unitaire',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='devis',
            name='produit',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Produits.produits'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='devis',
            name='quantite',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='devis',
            name='total',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='devisfact',
            name='date_creation',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='devisfact',
            name='remarque',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='devisfact',
            name='statut',
            field=models.CharField(choices=[('en_cours', 'En cours'), ('valide', 'Validé'), ('refuse', 'Refusé')], default='en_cours', max_length=10),
        ),
    ]
