# Generated by Django 2.2.7 on 2020-03-24 05:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("orders", "0003_order_number_of_containers")]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="number_of_containers",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        )
    ]