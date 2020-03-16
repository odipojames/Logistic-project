# Generated by Django 2.2.7 on 2020-02-05 15:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import utils.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("companies", "0006_auto_20200204_1808"),
    ]

    operations = [
        migrations.AlterModelManagers(name="cargoownercompany", managers=[]),
        migrations.AlterModelManagers(name="shypper", managers=[]),
        migrations.AlterModelManagers(name="transportercompany", managers=[]),
        migrations.RemoveField(model_name="cargoownercompany", name="account_number"),
        migrations.RemoveField(model_name="cargoownercompany", name="business_email"),
        migrations.RemoveField(model_name="cargoownercompany", name="business_name"),
        migrations.RemoveField(
            model_name="cargoownercompany", name="business_phone_no"
        ),
        migrations.RemoveField(model_name="cargoownercompany", name="business_type"),
        migrations.RemoveField(
            model_name="cargoownercompany", name="certificate_of_incorporation"
        ),
        migrations.RemoveField(model_name="cargoownercompany", name="company_director"),
        migrations.RemoveField(model_name="cargoownercompany", name="directors_id"),
        migrations.RemoveField(model_name="cargoownercompany", name="employees"),
        migrations.RemoveField(model_name="cargoownercompany", name="is_active"),
        migrations.RemoveField(model_name="cargoownercompany", name="location"),
        migrations.RemoveField(model_name="cargoownercompany", name="logo"),
        migrations.RemoveField(
            model_name="cargoownercompany", name="operational_regions"
        ),
        migrations.RemoveField(model_name="cargoownercompany", name="postal_code"),
        migrations.RemoveField(
            model_name="cargoownercompany", name="prefered_currency"
        ),
        migrations.RemoveField(model_name="shypper", name="account_number"),
        migrations.RemoveField(model_name="shypper", name="business_email"),
        migrations.RemoveField(model_name="shypper", name="business_name"),
        migrations.RemoveField(model_name="shypper", name="business_phone_no"),
        migrations.RemoveField(model_name="shypper", name="business_type"),
        migrations.RemoveField(
            model_name="shypper", name="certificate_of_incorporation"
        ),
        migrations.RemoveField(model_name="shypper", name="company_director"),
        migrations.RemoveField(model_name="shypper", name="directors_id"),
        migrations.RemoveField(model_name="shypper", name="employees"),
        migrations.RemoveField(model_name="shypper", name="is_active"),
        migrations.RemoveField(model_name="shypper", name="location"),
        migrations.RemoveField(model_name="shypper", name="logo"),
        migrations.RemoveField(model_name="shypper", name="operational_regions"),
        migrations.RemoveField(model_name="shypper", name="postal_code"),
        migrations.RemoveField(model_name="shypper", name="prefered_currency"),
        migrations.RemoveField(model_name="transportercompany", name="account_number"),
        migrations.RemoveField(model_name="transportercompany", name="business_email"),
        migrations.RemoveField(model_name="transportercompany", name="business_name"),
        migrations.RemoveField(
            model_name="transportercompany", name="business_phone_no"
        ),
        migrations.RemoveField(model_name="transportercompany", name="business_type"),
        migrations.RemoveField(
            model_name="transportercompany", name="certificate_of_incorporation"
        ),
        migrations.RemoveField(
            model_name="transportercompany", name="company_director"
        ),
        migrations.RemoveField(model_name="transportercompany", name="directors_id"),
        migrations.RemoveField(model_name="transportercompany", name="employees"),
        migrations.RemoveField(model_name="transportercompany", name="is_active"),
        migrations.RemoveField(model_name="transportercompany", name="location"),
        migrations.RemoveField(model_name="transportercompany", name="logo"),
        migrations.RemoveField(
            model_name="transportercompany", name="operational_regions"
        ),
        migrations.RemoveField(model_name="transportercompany", name="postal_code"),
        migrations.RemoveField(
            model_name="transportercompany", name="prefered_currency"
        ),
        migrations.CreateModel(
            name="Company",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("business_name", models.CharField(max_length=20, unique=True)),
                (
                    "business_type",
                    models.CharField(
                        choices=[
                            ("single", "single"),
                            ("Corporate", "Corporate"),
                            ("others", "others"),
                        ],
                        max_length=200,
                    ),
                ),
                ("account_number", models.CharField(max_length=50, unique=True)),
                ("prefered_currency", models.CharField(max_length=200)),
                ("logo", models.ImageField(upload_to="documents/")),
                (
                    "business_phone_no",
                    models.CharField(
                        max_length=20,
                        unique=True,
                        validators=[
                            utils.validators.validate_international_phone_number
                        ],
                    ),
                ),
                ("business_email", models.EmailField(max_length=254, unique=True)),
                ("postal_code", models.CharField(max_length=50, null=True)),
                (
                    "location",
                    models.CharField(help_text="Street, City, Country", max_length=200),
                ),
                (
                    "operational_regions",
                    models.CharField(
                        choices=[
                            ("locals", "locals"),
                            ("transit", "transit"),
                            ("both", "both"),
                        ],
                        max_length=30,
                    ),
                ),
                ("is_active", models.BooleanField(default=False)),
                (
                    "certificate_of_incorporation",
                    models.FileField(
                        upload_to="documents/",
                        validators=[utils.validators.validate_file_extension],
                    ),
                ),
                (
                    "directors_id",
                    models.FileField(
                        upload_to="documents/",
                        validators=[utils.validators.validate_file_extension],
                    ),
                ),
                ("is_shypper", models.BooleanField(default=True)),
                (
                    "company_director",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"abstract": False},
            managers=[("active_objects", django.db.models.manager.Manager())],
        ),
        migrations.AddField(
            model_name="cargoownercompany",
            name="company",
            field=models.OneToOneField(
                default=1,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="companies.Company",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="shypper",
            name="company",
            field=models.OneToOneField(
                default=1,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="companies.Company",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="transportercompany",
            name="company",
            field=models.OneToOneField(
                default=1,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="companies.Company",
            ),
            preserve_default=False,
        ),
    ]
