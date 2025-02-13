# Generated by Django 5.1.4 on 2025-01-11 16:25

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Produits', '0028_remove_bondecommande_fournisseur_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='devis',
            name='date_devis',
        ),
        migrations.RemoveField(
            model_name='devis',
            name='produits',
        ),
        migrations.RemoveField(
            model_name='devis',
            name='total',
        ),
        migrations.RemoveField(
            model_name='devis',
            name='valide',
        ),
        migrations.AddField(
            model_name='devis',
            name='createur',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='createur_devis', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='devis',
            name='date_creation',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='devis',
            name='date_expiration',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='devis',
            name='modificateur',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='modificateur_devis', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='devis',
            name='remarque',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='devis',
            name='remise_globale',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='devis',
            name='statut',
            field=models.CharField(choices=[('en_cours', 'En cours'), ('valide', 'Validé'), ('refuse', 'Refusé')], default='en_cours', max_length=10),
        ),
        migrations.CreateModel(
            name='DevisFact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantite', models.PositiveIntegerField()),
                ('prix_unitaire', models.DecimalField(decimal_places=2, max_digits=10)),
                ('remise_specifique', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('sous_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('produit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Produits.produits')),
            ],
        ),
        migrations.AddField(
            model_name='devis',
            name='devisfac',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='devisfac', to='Produits.devisfact'),
            preserve_default=False,
        ),
    ]
