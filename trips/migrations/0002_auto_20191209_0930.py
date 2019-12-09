# Generated by Django 2.2.7 on 2019-12-09 06:30

import django.contrib.postgres.fields.hstore
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
        ('trips', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trip',
            old_name='truck',
            new_name='trucks',
        ),
        migrations.CreateModel(
            name='TripInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('charges', django.contrib.postgres.fields.hstore.HStoreField()),
                ('description', models.CharField(max_length=1000)),
                ('trip', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='invoice', to='trips.Trip')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ratings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.CharField(max_length=1000)),
                ('points', models.IntegerField()),
                ('reviewee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='companies.Transporter')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='companies.CargoOwner')),
            ],
        ),
    ]
