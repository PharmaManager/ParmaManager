# Generated by Django 5.1.4 on 2025-01-10 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Produits', '0020_remove_bondecommande_client_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bondecommande',
            name='prix_unitaire',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
    ]
