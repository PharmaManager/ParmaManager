# Generated by Django 5.1.4 on 2025-01-15 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Produits', '0036_devis_client_alter_devisfact_client'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devis',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='devisfact',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
