# Generated by Django 5.1.4 on 2025-01-31 20:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Produits', '0051_alter_facture_client_uuid_alter_vente_uuid'),
        ('utilisateurs', '0003_compte_etat_compte_taille_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sujet', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='contact_images/')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('compte', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='utilisateurs.compte')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
