# Generated by Django 2.2.7 on 2020-02-15 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("authentication", "0005_auto_20200215_1153")]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="profile_picture",
            field=models.ImageField(
                default="staticfiles/images/profile.jpg", upload_to="documents/profile/"
            ),
        )
    ]
