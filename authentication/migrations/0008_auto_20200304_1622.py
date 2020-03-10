# Generated by Django 2.2.7 on 2020-03-04 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_auto_20200216_1923'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='biography',
        ),
        migrations.AddField(
            model_name='profile',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='id_or_passport',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='person_contact_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='person_contact_phone',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]