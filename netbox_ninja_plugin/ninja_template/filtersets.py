from django.db.models import Q
from django.db.models.query import QuerySet
from netbox.filtersets import NetBoxModelFilterSet
from utilities.filters import MultiValueCharFilter

from netbox_ninja_plugin.ninja_template.models import NinjaTemplate


class NinjaTemplateFilterSet(NetBoxModelFilterSet):

    object_types = MultiValueCharFilter(
        method="filter_by_key",
        field_name="object_types__in",
    )

    output_type = MultiValueCharFilter(
        method="filter_by_key",
        field_name="output_type__in",
    )

    def search(self, queryset: QuerySet, _, value: str) -> QuerySet:
        return queryset.filter(Q(name__icontains=value) | Q(code__icontains=value))

    def filter_by_key(
        self, queryset: QuerySet, field: str, object_ids: list[int]
    ) -> QuerySet[NinjaTemplate]:
        return queryset.filter(**{f"{field}": object_ids})

    class Meta:
        model = NinjaTemplate
        fields = [
            "name",
            "object_types",
            "output_type",
            "code",
        ]
