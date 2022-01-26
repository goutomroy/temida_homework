import uuid

from django.db import models


class BaseModel(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Source(BaseModel):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    tin = models.CharField(max_length=30, unique=True)
    company = models.CharField(max_length=55)
    total_amount = models.CharField(max_length=355)
    address = models.CharField(max_length=155)
    document_type = models.CharField(max_length=355)
    number_id = models.CharField(max_length=55)
    sell_for = models.CharField(max_length=155)
    parsing_start_ts = models.DateTimeField(default=None)
    parsing_end_ts = models.DateTimeField(default=None)


# class Tin(models.Model):
#     id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
#     source = models.OneToOneField(Source, on_delete=models.CASCADE)
#     updated_at = models.DateTimeField(default=None)
