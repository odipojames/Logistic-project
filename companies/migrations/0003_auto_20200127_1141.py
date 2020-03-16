# Generated by Django 2.2.7 on 2020-01-27 08:41

from django.db import migrations, models
import utils.validators


class Migration(migrations.Migration):

    dependencies = [("companies", "0002_auto_20200122_1242")]

    operations = [
        migrations.AlterField(
            model_name="personofcontact",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name="personofcontact",
            name="phone",
            field=models.CharField(
                max_length=20,
                unique=True,
                validators=[utils.validators.validate_international_phone_number],
            ),
        ),
    ]
