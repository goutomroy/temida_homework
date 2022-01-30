from django.contrib import admin

from tins.models import Source, Tin


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "tin",
        "company",
        "total_amount",
        "address",
        "document_type",
        "number_id",
        "is_exist",
        "sell_for",
        "start_ts",
        "parsing_ts",
    ]
    readonly_fields = ["id"]


@admin.register(Tin)
class TinAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "tin",
    ]
    readonly_fields = ["id"]
