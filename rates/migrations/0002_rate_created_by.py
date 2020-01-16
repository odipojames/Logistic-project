# Generated by Django 2.2.7 on 2020-01-15 13:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0002_auto_20200115_1621'),
        ('rates', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rate',
            name='created_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='companies.CargoOwnerCompany'),
            preserve_default=False,
        ),
    ]