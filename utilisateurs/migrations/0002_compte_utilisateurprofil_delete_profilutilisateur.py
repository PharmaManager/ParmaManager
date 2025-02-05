# Generated by Django 5.1.4 on 2025-01-26 12:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilisateurs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Compte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('administrateur', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='compte', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UtilisateurProfil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('est_admin', models.BooleanField(default=False)),
                ('compte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='utilisateurs', to='utilisateurs.compte')),
                ('utilisateur', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profil', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='ProfilUtilisateur',
        ),
    ]
