# Generated by Django 5.0.6 on 2024-06-28 14:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mps', '0001_initial'),
        ('polling_station', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='County',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, unique=True)),
                ('constituency_count', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Constituency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
                ('registeredvoter_count', models.IntegerField(default=0)),
                ('mp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='constituencies', to='mps.memberofparliament')),
                ('polling_station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='constituencies', to='pollingStation.pollingstation')),
            ],
        ),
    ]
