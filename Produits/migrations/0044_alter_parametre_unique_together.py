# Generated by Django 5.1.4 on 2025-01-28 10:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Produits', '0043_parametre_remarque'),
        ('utilisateurs', '0002_compte_utilisateurprofil_delete_profilutilisateur'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='parametre',
            unique_together={('compte',)},
        ),
    ]
