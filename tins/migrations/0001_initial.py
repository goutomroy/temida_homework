# Generated by Django 4.0.1 on 2022-01-30 12:32

import datetime
import uuid

from django.db import migrations, models
from django.utils.timezone import utc

import tins.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Source",
            fields=[
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("tin", models.CharField(max_length=30, unique=True)),
                ("company", models.CharField(max_length=55)),
                ("total_amount", models.CharField(max_length=355)),
                ("address", models.CharField(max_length=155)),
                ("document_type", models.CharField(max_length=355)),
                ("number_id", models.CharField(max_length=55)),
                ("sell_for", models.CharField(max_length=155)),
                ("is_exist", models.BooleanField(default=False)),
                ("start_ts", models.DateField()),
                ("parsing_ts", models.DateTimeField()),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Tin",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "tin",
                    models.CharField(
                        max_length=55, validators=[tins.models.validate_tin]
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "updated",
                    models.DateTimeField(
                        default=datetime.datetime(
                            2022, 1, 30, 12, 32, 55, 912099, tzinfo=utc
                        )
                    ),
                ),
            ],
        ),
    ]
