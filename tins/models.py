import re
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Source(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    tin = models.CharField(max_length=30, unique=True)
    company = models.CharField(max_length=55)
    total_amount = models.CharField(max_length=355)
    address = models.CharField(max_length=155)
    document_type = models.CharField(max_length=355)
    number_id = models.CharField(max_length=55)
    sell_for = models.CharField(max_length=155)
    is_exist = models.BooleanField(default=False)
    start_ts = models.DateField()
    parsing_ts = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)


def validate_tin(value):
    regex = "^[a-zA-Z]{0,5}[0-9]{5,10}$"
    results = re.findall(regex, value)
    if not results:
        raise ValidationError(
            _(
                "Tin should start with string of length 0-5 and followed by digits of length 5-10"  # noqa
            ),
        )
    return results[0]


class Tin(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    tin = models.CharField(max_length=55, validators=[validate_tin])
    updated = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
