# Generated by Django 4.0.1 on 2022-01-30 12:37

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tins", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tin",
            name="updated",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
