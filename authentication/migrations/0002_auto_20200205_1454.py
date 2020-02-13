# Generated by Django 2.2.7 on 2020-02-05 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='title',
            field=models.CharField(choices=[('transporter_director', 'transporter_director'), ('cargo_owner_director', 'cargo_owner_director'), ('driver', 'driver'), ('admin', 'admin'), ('staff', 'staff')], help_text="User's role within employer's organization.", max_length=100, unique=True),
        ),
    ]
