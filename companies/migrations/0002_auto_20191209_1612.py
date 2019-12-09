# Generated by Django 2.2.7 on 2019-12-09 13:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cargoowner',
            name='company_location',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='cargo_owners', to='locations.Location'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='transporter',
            name='company_location',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='transporters', to='locations.Location'),
            preserve_default=False,
        ),
    ]
