from django.contrib import admin

from tins.models import Source


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
        "sell_for",
    ]
    readonly_fields = ["id"]
