# Generated by Django 5.1.4 on 2025-01-24 18:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfilUtilisateur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('espace', models.CharField(max_length=100, unique=True)),
                ('utilisateur', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profil', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
