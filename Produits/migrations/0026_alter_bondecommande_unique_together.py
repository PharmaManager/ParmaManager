# Generated by Django 5.1.4 on 2025-01-10 18:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Produits', '0025_alter_bondecommande_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bondecommande',
            unique_together=set(),
        ),
    ]
