# Generated by Django 2.2.7 on 2020-03-18 11:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("trips", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "name",
                    models.CharField(
                        choices=[
                            ("P", "pending"),
                            ("A", "accepted"),
                            ("L", "loaded"),
                            ("S", "started"),
                            ("O", "on journey"),
                            ("STP", "stopped"),
                            ("F", "finished"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "triggered_by",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_event",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "trip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="trips",
                        to="trips.Trip",
                    ),
                ),
            ],
            options={"abstract": False},
        )
    ]
